import io
import json
import os
from textwrap import indent


class ScratchCodeFormatter:
    @staticmethod
    def format(json_object: dict) -> str:
        with io.StringIO() as output:
            for target in json_object['targets']:
                if not target['isStage']:
                    ScratchCodeFormatter._format_blocks(target, output)
                    ScratchCodeFormatter._format_comments(target, output)
            return output.getvalue()

    @staticmethod
    def _format_blocks(target: dict, output: io.StringIO):
        blocks = target['blocks']
        for block_id in blocks:
            block = blocks[block_id]
            if 'topLevel' in block and block['topLevel']:
                stack_text = ScratchCodeFormatter._get_stack_text(target, block_id)
                if stack_text:
                    output.write(stack_text)
                    if stack_text[-0] != '\n':
                        output.write('\n')

    @staticmethod
    def _get_stack_text(target: dict, block_id: str, indent: int = 0) -> str:
        blocks = target['blocks']
        with io.StringIO() as output:
            while True:
                block = blocks[block_id]
                block_text = ScratchCodeFormatter._get_block_text(target, block_id, indent=indent)
                if block_text:
                    ScratchCodeFormatter._write_indent(output, indent)
                    output.write(block_text)
                    if block_text[-1] != '\n':
                        output.write('\n')

                block_id = block['next']
                if not block_id:
                    break
            return output.getvalue()

    @staticmethod
    def _get_block_text(target: dict, block_id: str, get_shadow: bool = False, indent: int = 0) -> str:
        blocks = target['blocks']
        comments = target['comments']
        block = blocks[block_id]
        if block['shadow'] and not get_shadow:
            return ''

        inputs = block['inputs']

        with io.StringIO() as output:
            substack_block_id = None
            substack2_block_id = None
            if 'mutation' in block:
                if block['opcode'] == 'procedures_call':
                    output.write(ScratchCodeFormatter._get_string('procedures_call'))

                output.write(ScratchCodeFormatter._get_mutation(target, block['mutation'], inputs))
            else:
                parameters = dict()

                fields = block['fields']
                for field in fields:
                    values = fields[field]
                    parameters[field] = values[0]

                for input in inputs:
                    if input == 'SUBSTACK':
                        values = inputs[input]
                        substack_block_id = values[1]
                        continue

                    if input == 'SUBSTACK2':
                        values = inputs[input]
                        substack2_block_id = values[1]
                        continue

                    values = inputs[input]
                    value = values[1]
                    if type(value) is list:
                        parameters[input] = value[1]
                    else:
                        parameters[input] = ScratchCodeFormatter._get_block_text(target, value, get_shadow=True)

                for parameter in parameters:
                    parameters[parameter] = ScratchCodeFormatter._get_parameter_value(block, parameter, parameters[parameter])

                opcode = block['opcode']
                format_string = ScratchCodeFormatter._get_string(opcode)
                if format_string != opcode:
                    try:
                        output.write(format_string.format(**parameters))
                    except KeyError:
                        tokens = [format_string]
                        for key in parameters:
                            value = parameters[key]
                            tokens.append(f'{key}={value}')
                        output.write(' '.join(tokens))
                else:
                    tokens = [opcode]
                    for key in parameters:
                        value = parameters[key]
                        tokens.append(f'{key}={value}')
                    output.write(' '.join(tokens))

            if 'comment' in block:
                comment_id = block['comment']
                if comment_id in comments:
                    comment = comments[comment_id]
                    text = ScratchCodeFormatter._get_comment_text(comment)
                    output.write('  # '.join(['', *text.splitlines()]))

            if substack_block_id:
                output.write('\n')
                output.write(ScratchCodeFormatter._get_stack_text(target, substack_block_id, indent + 1))

            if substack2_block_id:
                ScratchCodeFormatter._write_indent(output, indent)
                output.write(ScratchCodeFormatter._get_string('control_else'))
                output.write('\n')
                output.write(ScratchCodeFormatter._get_stack_text(target, substack2_block_id, indent + 1))

            return output.getvalue()

    @staticmethod
    def _get_mutation(target: dict, mutation: dict, inputs: dict):
        tokens = []
        for argument_id in json.loads(mutation['argumentids']):
            if argument_id in inputs:
                values = inputs[argument_id]
                value = values[1]
                if type(value) is list:
                    tokens.append(value[1])
                else:
                    if value:
                        tokens.append(ScratchCodeFormatter._get_block_text(target, value, get_shadow=True))
                    else:  # handle missing boolean argument in my block
                        tokens.append(' ')
            else:  # handle missing boolean argument in my block
                tokens.append(' ')
                pass

        for i in range(len(tokens)):
            if tokens[i] is None or not tokens[i]:  # handle missing number or text argument in my block
                tokens[i] = ' '

        mutation_string = mutation['proccode']
        mutation_string = mutation_string.replace('%s', '{}')
        mutation_string = mutation_string.replace('%b', '{}')
        mutation_string = mutation_string.format(*tokens)
        return mutation_string

    _parameter_mappings = None

    @staticmethod
    def _get_parameter_value(block: dict, parameter: str, value: str) -> str:
        opcode = block['opcode']

        if parameter == 'field_flippersound_sound-selector':
            return json.loads(value)['name']

        if ScratchCodeFormatter._parameter_mappings is None:
            script_dir = os.path.abspath(os.path.dirname(__file__))
            mappings_json_path = os.path.join(script_dir, 'mappings.json')
            with open(mappings_json_path, 'rt') as mappings_json:
                languages = json.load(mappings_json)
                ScratchCodeFormatter._parameter_mappings = languages['en-us']

        for mapping in ScratchCodeFormatter._parameter_mappings:
            is_match = False
            if 'opcode' in mapping:
                mapping_opcode = mapping['opcode']
                if type(mapping_opcode) is list:
                    if opcode in mapping_opcode:
                        is_match = True
                else:
                    if mapping_opcode == opcode:
                        is_match = True

            if 'opcode_startswith' in mapping:
                opcode_startswith = mapping['opcode_startswith']
                if opcode.startswith(opcode_startswith):
                    is_match = True

            if not is_match:
                continue

            parameters = mapping['parameters']
            for mapping_parameter in parameters:
                if parameter in mapping_parameter:
                    mapping_values = mapping_parameter[parameter]
                    if value in mapping_values:
                        return mapping_values[value]

        return value

    _strings = None

    @staticmethod
    def _format_comments(target: dict, output: io.StringIO):
        comments = target['comments']
        for comment_id in comments:
            comment = comments[comment_id]
            if 'blockId' in comment and comment['blockId'] is not None:
                continue

            text = ScratchCodeFormatter._get_comment_text(comment)
            text = indent(text, '# ', lambda line: True)
            output.write(text)
            if text[-1] != '\n':
                output.write('\n')
            output.write('\n')

    @staticmethod
    def _get_comment_text(comment: str) -> str:
        return comment['text'] if 'text' in comment else ''

    @staticmethod
    def _get_string(input: str) -> str:
        if type(input) is not str:
            return input

        if ScratchCodeFormatter._strings is None:
            script_dir = os.path.abspath(os.path.dirname(__file__))
            strings_json_path = os.path.join(script_dir, 'strings.json')
            with open(strings_json_path, 'rt') as strings_json:
                languages = json.load(strings_json)
                ScratchCodeFormatter._strings = languages['en-us']

        if input in ScratchCodeFormatter._strings:
            return ScratchCodeFormatter._strings[input]
        else:
            return input

    @staticmethod
    def _write_indent(output: io.StringIO, indent: int = 0):
        output.write(' ' * (indent * 3))
