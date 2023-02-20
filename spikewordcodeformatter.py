import io
import json


class SpikeWordCodeFormatter:
    @staticmethod
    def format(json_object):
        with io.StringIO() as output:
            for target in json_object['targets']:
                if not target['isStage']:
                    SpikeWordCodeFormatter._format_blocks(target['blocks'], output)
            return output.getvalue()

    @staticmethod
    def _format_blocks(blocks, output):
        for block_id in blocks:
            block = blocks[block_id]
            if block['topLevel']:
                stack_text = SpikeWordCodeFormatter._get_stack_text(blocks, block_id)
                if stack_text:
                    output.write(stack_text)
                    if stack_text[-0] != '\n':
                        output.write('\n')


    @staticmethod
    def _get_stack_text(blocks, block_id, indent: int = 0) -> str:
        with io.StringIO() as output:
            while True:
                block = blocks[block_id]
                block_text = SpikeWordCodeFormatter._get_block_text(blocks, block_id)
                if block_text:
                    SpikeWordCodeFormatter._write_indent(output, indent)
                    output.write(block_text)
                    if block_text[-1] != '\n':
                        output.write('\n')

                block_id = block['next']
                if not block_id:
                    break
            return output.getvalue()

    @staticmethod
    def _get_block_text(blocks, block_id, get_shadow: bool = False, indent: int = 0) -> str:
        block = blocks[block_id]
        if block['shadow'] and not get_shadow:
            return ''

        inputs = block['inputs']

        with io.StringIO() as output:
            if 'mutation' in block:
                if block['opcode'] == 'procedures_call':
                    output.write(SpikeWordCodeFormatter._get_string('procedures_call'))

                output.write(SpikeWordCodeFormatter._get_mutation(blocks, block['mutation'], inputs))
            else:
                parameters = dict()

                fields = block['fields']
                for field in fields:
                    values = fields[field]
                    value = values[0]
                    parameters[field] = value

                substack_block_id = None
                substack2_block_id = None
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
                        parameters[input] = SpikeWordCodeFormatter._get_block_text(blocks, value, get_shadow=True)

                opcode = block['opcode']
                format_string = SpikeWordCodeFormatter._get_string(opcode)
                if format_string != opcode:
                    output.write(format_string.format(**parameters))
                else:
                    tokens = [opcode]
                    for key in parameters:
                        value = parameters[key]
                        tokens.append(f'{key}={value}')
                    output.write(' '.join(tokens))

                if substack_block_id:
                    output.write('\n')
                    output.write(SpikeWordCodeFormatter._get_stack_text(blocks, substack_block_id, indent + 1))

                if substack2_block_id:
                    SpikeWordCodeFormatter._write_indent(output, indent)
                    output.write(SpikeWordCodeFormatter._get_string('control_else'))
                    output.write('\n')
                    output.write(SpikeWordCodeFormatter._get_stack_text(blocks, substack2_block_id, indent + 1))

            return output.getvalue()

    @staticmethod
    def _get_mutation(blocks, mutation, inputs):
        tokens = []
        for argument_id in SpikeWordCodeFormatter._parse_argument_ids(mutation['argumentids']):
            values = inputs[argument_id]
            value = values[1]
            if type(value) is list:
                tokens.append(value[1])
            else:
                tokens.append(SpikeWordCodeFormatter._get_block_text(blocks, values[1], get_shadow=True))

        mutation_string = mutation['proccode']
        mutation_string = mutation_string.replace('%s', '{}')
        mutation_string = mutation_string.format(*tokens)
        return mutation_string

    @staticmethod
    def _parse_argument_ids(argument_ids: str) -> list:
        # example: ["|dzTU:a[54zuspL$r67$","GeG.80K5h$OI96s[vrXa"]

        argument_ids = argument_ids[1:-1]  # remove square brackets

        argument_id_list = []
        for argument_id in argument_ids.split(','):
            argument_id = argument_id[1:-1]  # remove quotation marks
            argument_id_list.append(argument_id)

        return argument_id_list

    @staticmethod
    def _get_string(input: str) -> str:
        if type(input) is not str:
            return input

        with open('strings.json', 'rt') as strings_json:
            languages = json.load(strings_json)
            language = languages['en-us']
            if input in language:
                return language[input]
            else:
                return input

    @staticmethod
    def _write_indent(output, indent: int = 0):
        output.write(' ' * (indent * 3))
