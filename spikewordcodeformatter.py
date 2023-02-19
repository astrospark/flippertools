import io


class SpikeWordCodeFormatter:
    @staticmethod
    def format(json_object):
        with io.StringIO() as output:
            for target in json_object['targets']:
                if not target['isStage']:
                    SpikeWordCodeFormatter.format_blocks(target['blocks'], output)
            return output.getvalue()

    @staticmethod
    def format_blocks(blocks, output):
        for block_id in blocks:
            SpikeWordCodeFormatter.format_block(blocks, block_id, output)

    @staticmethod
    def format_block(blocks, block_id, output):
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
        for input in inputs:
            tokens.append(input)
            tokens.append('=')
            values = inputs[input]
            value = values[1]
            if type(value) is list:
                tokens.append(value[1])
            else:
                tokens.append('[')
                tokens.append(SpikeWordCodeFormatter.format_value_block(blocks, values[1]))
                tokens.append(']')

        tokens.append('\n')
        output.write(' '.join(tokens))

    @staticmethod
    def format_value_block(blocks, block_id) -> str:
        block = blocks[block_id]
        tokens = [block['opcode']]

        fields = block['fields']
        for field in fields:
            # tokens.append(field)
            # tokens.append('=')
            values = fields[field]
            value = values[0]
            tokens.append(value)

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
                tokens.append(SpikeWordCodeFormatter.format_value_block(blocks, values[1]))
                tokens.append(']')

        return ' '.join(tokens)
