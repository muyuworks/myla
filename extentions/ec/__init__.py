import json
from muyu import tools
from muyu.tools import Context

class ECTool(tools.Tool):
    def __init__(self, device='cpu') -> None:
        super().__init__()

        self.device = device

    async def execute(self, context: Context) -> None:
        docs = None
        for msg in context.messages:
            if msg.get('type') == 'docs':
                docs = msg['content']
                break
        
        if not docs:
            return
        
        docs = json.loads(docs)
        print(docs)
        #

    