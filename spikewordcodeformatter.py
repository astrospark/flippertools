import io


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
                SpikeWordCodeFormatter._format_stack(blocks, block_id, output)
                output.write('\n')

    @staticmethod
    def _format_stack(blocks, block_id, output, indent: int = 0):
        while True:
            block = blocks[block_id]
            SpikeWordCodeFormatter._format_block(blocks, block_id, output, indent)

            block_id = block['next']
            if not block_id:
                break

    @staticmethod
    def _format_block(blocks, block_id, output, indent: int = 0):
        block = blocks[block_id]
        if block['shadow']:
            return

        inputs = block['inputs']

        if 'mutation' in block:
            SpikeWordCodeFormatter._write_indent(output, indent)
            output.write('run my block: ')
            output.write(SpikeWordCodeFormatter._get_mutation(blocks, block['mutation'], inputs))
            output.write('\n')
        else:
            tokens = [block['opcode']]

            fields = block['fields']
            for field in fields:
                tokens.append(field)
                tokens.append('=')
                values = fields[field]
                value = values[0]
                tokens.append(value)

            substack_block_id = None
            for input in inputs:
                if input == 'SUBSTACK':
                    values = inputs[input]
                    substack_block_id = values[1]
                    break

                tokens.append(input)
                tokens.append('=')
                values = inputs[input]
                value = values[1]
                if type(value) is list:
                    tokens.append(value[1])
                else:
                    tokens.append('[' + SpikeWordCodeFormatter._get_value_block(blocks, value) + ']')

            tokens.append('\n')
            SpikeWordCodeFormatter._write_indent(output, indent)
            output.write(' '.join(tokens))

            if substack_block_id:
                SpikeWordCodeFormatter._format_stack(blocks, substack_block_id, output, indent + 1)

    @staticmethod
    def _get_value_block(blocks, block_id) -> str:
        block = blocks[block_id]
        tokens = [block['opcode']]

        fields = block['fields']
        for field in fields:
            # tokens.append(field)
            # tokens.append('=')
            values = fields[field]
            value = values[0]
            tokens.append(str(value))

        inputs = block['inputs']
        for input in inputs:
            tokens.append(input)
            tokens.append('=')
            values = inputs[input]
            value = values[1]
            if type(value) is list:
                tokens.append(value[1])
            else:
                tokens.append('[' + SpikeWordCodeFormatter._get_value_block(blocks, values[1]) + ']')

        return ' '.join(tokens)

    @staticmethod
    def _get_mutation(blocks, mutation, inputs):
        tokens = []
        for argument_id in SpikeWordCodeFormatter._parse_argument_ids(mutation['argumentids']):
            values = inputs[argument_id]
            value = values[1]
            if type(value) is list:
                tokens.append(value[1])
            else:
                tokens.append(SpikeWordCodeFormatter._get_value_block(blocks, values[1]))

        mutation_string = mutation['proccode']
        mutation_string = mutation_string.replace('%s', '[{}]')
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
    def _write_indent(output, indent: int = 0):
        output.write(' ' * (indent * 3))
