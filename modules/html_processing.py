import os

def generate_html(json_data, output_file="blocks.html"):
    html_template = """<!DOCTYPE html>
<html>
<head>
    <title>Blocks Collection</title>
    <style>
        fieldset {{
            margin: 20px;
            border: 2px solid #ccc;
            padding: 10px;
        }}
        .color-box {{
            width: 100px;
            height: 100px;
            text-align: center;
            line-height: 100px;
            display: inline-block;
        }}
        .block {{
            border: 1px solid #000;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""

    blocks_content = []

    def process_block(block_id, block_data):
        # Calculate block dimensions
        coords = block_data.get('coordinatesXY', [])
        if len(coords) < 4:
            return ""
            
        x_values = [p[0] for p in coords]
        y_values = [p[1] for p in coords]
        width = max(x_values) - min(x_values)
        height = max(y_values) - min(y_values)
        
        # Get colors and text
        colors = block_data.get('colors', [])
        text = block_data.get('text', '')
        
        # Generate color boxes with hex codes
        colors_html = "".join(
            f'<div class="color-box" style="background-color: {color};">{color}</div>\n'
            for color in colors
        )
        
        # Generate block HTML
        return f"""
        <fieldset>
            <legend>{block_id}</legend>
            <div class="colors">{colors_html}</div>
            <div class="block" style="width: {width}px; height: {height}px;">
                {text}
            </div>
        </fieldset>
        """

    def traverse_blocks(blocks, parent_id=""):
        for block_id, block_data in blocks.items():
            full_id = f"{parent_id}_{block_id}" if parent_id else block_id
            blocks_content.append(process_block(full_id, block_data))
            
            if block_data.get('children'):
                traverse_blocks(block_data['children'], full_id)

    traverse_blocks(json_data['block_00']['children'])
    
    with open("blocks.html", 'w', encoding='utf-8') as f:
        f.write(html_template.format(content="\n".join(blocks_content)))
    
    return "blocks.html"