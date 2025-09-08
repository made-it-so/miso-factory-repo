# python_agent_runner/agents/genesis_agent.py
import os

class GenesisAgent:
    def create_website(self, brief):
        """
        Takes a project brief dictionary and generates a simple HTML file
        in a web-accessible static directory.
        """
        goal = brief.get('goal', 'My Website')
        content = brief.get('content', 'Welcome to my new site.')
        vibe = brief.get('vibe', 'A clean and simple style.')
        action = brief.get('action', 'Click Here')

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{goal}</title>
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: auto; }}
        header {{ background: #f4f4f4; padding: 1rem; text-align: center; }}
        section {{ padding: 1rem; border-bottom: 1px solid #ddd; }}
        footer {{ text-align: center; padding: 1rem; margin-top: 20px; background: #333; color: #fff; }}
        .cta-button {{ background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <header><h1>{goal}</h1><p>Style notes: {vibe}</p></header>
    <section id="main-content"><h2>Main Content</h2><p>{content}</p></section>
    <footer><a href="#" class="cta-button">{action}</a></footer>
</body>
</html>
"""
        # Define a web-accessible output path
        output_dir = 'python_agent_runner/blueprints/ui/static/output'
        output_filename = 'output.html'
        output_path = os.path.join(output_dir, output_filename)
        
        # The URL the browser will use to access the file
        preview_url = f'/ui/static/output/{output_filename}'

        try:
            os.makedirs(output_dir, exist_ok=True) # Ensure the output directory exists
            with open(output_path, 'w') as f:
                f.write(html_template)
            return {"status": "Success", "preview_url": preview_url}
        except Exception as e:
            return {"status": f"Error: {e}", "preview_url": None}
