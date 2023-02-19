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

        tokens = [block['opcode']]

        fields = block['fields']
        for field in fields:
            tokens.append(field)
            tokens.append('=')
            values = fields[field]
            value = values[0]
            tokens.append(value)

        inputs = block['inputs']
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
                tokens.append('[')
                tokens.append(SpikeWordCodeFormatter._get_value_block(blocks, value))
                tokens.append(']')

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
                tokens.append('[')
                tokens.append(SpikeWordCodeFormatter._get_value_block(blocks, values[1]))
                tokens.append(']')

        return ' '.join(tokens)

    @staticmethod
    def _write_indent(output, indent: int = 0):
        output.write(' ' * (indent * 3))
