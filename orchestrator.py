import json
from prompt_assistant import prompt_assistant
from memory.memory import search_memory
from web_search.search import search_web
import importlib.util
import os
import re

def get_available_tools() -> list:
    """
    Discover all available tools by checking directories in the tools folder.
    Returns a list of tool names and their descriptions.
    """
    tools_dir = "tools"
    available_tools = []
    
    if os.path.exists(tools_dir) and os.path.isdir(tools_dir):
        for item in os.listdir(tools_dir):
            tool_path = os.path.join(tools_dir, item)
            meta_path = os.path.join(tool_path, "meta.json")
            
            if os.path.isdir(tool_path) and os.path.exists(os.path.join(tool_path, "run.py")):
                tool_info = {"name": item}
                
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, 'r') as meta_file:
                            metadata = json.load(meta_file)
                            tool_info.update(metadata)
                    except json.JSONDecodeError:
                        pass
                
                available_tools.append(tool_info)
    
    return available_tools

def get_tool_metadata(tool_name: str) -> dict:
    """Get metadata for a specific tool"""
    meta_path = f"tools/{tool_name}/meta.json"
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r') as meta_file:
                return json.load(meta_file)
        except json.JSONDecodeError:
            pass
    return {}

def find_best_tool(user_input: str, available_tools: list) -> dict:
    """Find the most relevant tool for the user input"""
    if not available_tools:
        return None
    
    tools_info = "\n".join([f"- {tool.get('name')}: {tool.get('description', 'No description')}" 
                           for tool in available_tools])
    
    prompt = f"""
    [USER INPUT]: {user_input}
    
    [AVAILABLE TOOLS]:
    {tools_info}
    
    Based on the user input, identify the most suitable tool from the available tools list.
    Respond with a JSON containing:
    - tool_name: The name of the selected tool
    - reason: Brief explanation for selecting this tool
    
    If no tool is suitable, respond with:
    {{"tool_name": "none", "reason": "No suitable tool available"}}
    """
    
    response = prompt_assistant(prompt)
    try:
        result = json.loads(response)
        tool_name = result.get("tool_name")
        if tool_name and tool_name != "none":
            return next((tool for tool in available_tools if tool["name"] == tool_name), None)
    except json.JSONDecodeError:
        pass
    
    return None

def extract_tool_args(user_input: str, tool_metadata: dict) -> dict:
    """Extract arguments for a tool based on its metadata and user input"""
    if not tool_metadata or "args" not in tool_metadata:
        return {}
    
    args_spec = tool_metadata["args"]
    args_description = ""
    
    if isinstance(args_spec, dict):
        args_description = "\n".join([f"- {arg}: {desc}" for arg, desc in args_spec.items()])
        arg_names = list(args_spec.keys())
    elif isinstance(args_spec, list):
        args_description = "\n".join([f"- {arg}" for arg in args_spec])
        arg_names = args_spec
    else:
        return {}
    
    prompt = f"""
    [USER INPUT]: {user_input}
    
    [REQUIRED ARGUMENTS]:
    {args_description}
    
    Extract the values for the required arguments from the user input.
    Respond with a JSON containing the argument names and their extracted values.
    If a required argument is not found in the user input, make a reasonable inference.
    """
    
    response = prompt_assistant(prompt)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {arg: "" for arg in arg_names}

def run_tool(tool_name: str, args: dict) -> str:
    tool_path = f"tools/{tool_name}/run.py"
    spec = importlib.util.spec_from_file_location("tool_module", tool_path)
    tool_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool_module)
    return tool_module.run(args)

def generate_search_prompt(user_input: str) -> str:
    """Generate an optimized search prompt based on user input"""
    prompt = f"""
    [USER INPUT]: {user_input}
    
    Generate a concise search query that will help find the most relevant information to answer the user's question or request.
    The search query should:
    1. Extract key terms and concepts
    2. Be specific enough to yield precise results
    3. Not include unnecessary words like "find" or "search for"
    4. Focus on factual information needed
    
    Return only the search query text, nothing else.
    """
    
    search_query = prompt_assistant(prompt).strip()
    search_query = re.sub(r'^["\'](.*)["\']$', r'\1', search_query)
    return search_query

def orchestrate(user_input: str) -> str:
    memory = search_memory(user_input)
    context = "\n".join(memory)
    
    available_tools = get_available_tools()
    
    tools_info = []
    for tool in available_tools:
        desc = tool.get("description", "No description available")
        args_info = ""
        if "args" in tool:
            if isinstance(tool["args"], dict):
                args_info = f" (Args: {', '.join(tool['args'].keys())})"
            elif isinstance(tool["args"], list):
                args_info = f" (Args: {', '.join(tool['args'])})"
            else:
                args_info = " (Args available)"
        tools_info.append(f"{tool['name']}: {desc}{args_info}")
    
    tools_list_str = "\n".join([f"- {info}" for info in tools_info])

    prompt = f"""
    [USER INPUT]: {user_input}

    [MEMORY CONTEXT]: {context}

    [AVAILABLE TOOLS]:
    {tools_list_str}

    Based on the above, decide what to do. Respond with a JSON containing:
    - action: "respond" (if the user input can be answered directly based on the memory context),
               "web_search" (if additional information from the web is required to answer the user input),
               or "run_tool" (if a specific tool needs to be executed to fulfill the user request).
    - tool_name: (if applicable, specify the tool to be used when action is "run_tool". Must be one of the available tools)
    - args: (if applicable, provide the arguments required for the tool when action is "run_tool")
    - response: (used only if action is "respond", provide the direct response to the user)
    
    Ensure that the tool chosen is appropriate for the user input and is one of the available tools. If no suitable tool is available, use "web_search" or "respond" instead.

    Example:
    {{"action": "run_tool", "tool_name": "get_weather", "args": {{"location": "New York"}}, "response": ""}}
    """

    response = prompt_assistant(prompt)
    try:
        plan = json.loads(response)
    except json.JSONDecodeError:
        return "Failed to parse plan."

    action = plan.get("action")
    print(f"Action: {action}")

    if action == "respond":
        return plan.get("response", "")
    elif action == "web_search":
        search_query = generate_search_prompt(user_input)
        print(f"Search query: {search_query}")
        web_result = search_web(search_query)

        synthesis_prompt = f"""
        [USER QUESTION]: {user_input}
        [WEB SEARCH RESULTS]: {web_result}
        
        Based on the web search results, provide a comprehensive answer to the user's question.
        Focus on accuracy and relevance. Cite specific information from the search results.
        If the search results don't contain enough information to answer the question, acknowledge this limitation.
        """
        
        final_response = prompt_assistant(synthesis_prompt)
        return final_response
    elif action == "run_tool":
        tool_name = plan.get("tool_name")
        
        if "args" not in plan or not plan["args"]:
            tool_metadata = get_tool_metadata(tool_name)
            args = extract_tool_args(user_input, tool_metadata)
        else:
            args = plan.get("args", {})
        
        print(f"Running tool: {tool_name} with args: {args}")
        return run_tool(tool_name, args)
    else:
        return "Unknown action."
