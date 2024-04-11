#!/usr/bin/python3
import sys
import re
import logging

logging.basicConfig(level=logging.DEBUG)

all_chains: dict = {}

default_chain_list = ['input', 'forward', 'output']

input_string = sys.stdin.read()
line_list = input_string.splitlines()
current_table = None
current_chain = None
for line in line_list:
    token_list = line.split()

    # Skip empty line 
    if not token_list or '}' in line:
        continue
    
    # Parse table information
    if token_list[0] == 'table':
        # current table in form 'name (family)'
        current_table = f'{token_list[2]} ({token_list[1]})'
        logging.debug(f'current_table: {current_table}')
        if current_table not in all_chains:  # Check if the current table exists in all_chains
            all_chains[current_table] = {}  # Initialize the dictionary for the current table if it doesn't exist
        continue

    # Parse chain information
    if token_list[0] == 'chain':
        current_chain = token_list[1]  # Update current_chain here
        logging.debug(f'current_chain: {current_chain}')
        continue

    # Parse rules information
    if 'jump' in token_list:
        jump_index = token_list.index('jump')
        destination_chain = token_list[jump_index + 1]
        rule_body = ' '.join(token_list)  # Extract the rule body before the 'jump'
        logging.debug(f'jump_index: {jump_index}, destination_chain: {destination_chain}, rule_body: {rule_body}')
        if current_table not in all_chains:
            all_chains[current_table] = {}
        if current_chain not in all_chains[current_table]:
            all_chains[current_table][current_chain] = []
        all_chains[current_table][current_chain].append({'rule_body': rule_body, 'jump': destination_chain})
    else:
        rule_body = ' '.join(token_list)
        logging.debug(f'rule_body: {rule_body}')
        if current_table not in all_chains:
            all_chains[current_table] = {}
        if current_chain not in all_chains[current_table]:
            all_chains[current_table][current_chain] = []
        all_chains[current_table][current_chain].append({'rule_body': rule_body})


logging.debug(all_chains)


def get_node_name(table_name, chain_name):
    return re.sub('[^a-zA-Z0-9]', '', table_name) + '_' + re.sub('[^a-zA-Z0-9]', '', chain_name)


def get_port_name(rule_index):
    return "rule_" + str(rule_index)


output = """digraph {
    graph [pad="0.5", nodesep="0.5", ranksep="2"];
    node [shape=plain]
    rankdir=LR;

"""

# Process diagram connections
logging.debug('Processing diagram connections')

for table in all_chains:
    logging.debug(f'table: {table}')
    for chain in all_chains[table]:
        logging.debug(f'chain: {chain}')
        for i in range(len(all_chains[table][chain])):
            rule = all_chains[table][chain][i]
            if 'jump' in rule:
                source_node = get_node_name(table, chain) + ':' + get_port_name(i)
                target_node = get_node_name(table, rule['jump']) + ':begin'
                output += source_node + """ -> """ + target_node + """;
"""

# Generate node definitions
logging.debug('Generating node definitions')

for table in all_chains:
    logging.debug(f'table: {table}')
    for chain in all_chains[table]:
        logging.debug(f'chain: {chain}')
        node_name = get_node_name(table, chain)
        logging.debug(f'node_name: {node_name}')
        tmp_body = node_name + """ [label=<<table border="0" cellborder="1" cellspacing="0">"""
        if chain in default_chain_list:
            tmp_body += """
  <tr><td bgcolor="red"><i>""" + chain + """</i></td></tr>
  <tr><td port="begin" bgcolor="tomato"><i>""" + table + """</i></td></tr>"""
        else:
            tmp_body += """
  <tr><td><i>""" + chain + """</i></td></tr>
  <tr><td port="begin"><i>""" + table + """</i></td></tr>"""
        for i in range(len(all_chains[table][chain])):
            rule = all_chains[table][chain][i]
            tmp_body += """
  <tr><td port="""
            if 'hook' in rule['rule_body']:
                tmp_body += "\"" + get_port_name(i) + "\" bgcolor=\"lightgreen\""
            else:
                tmp_body += "\"" + get_port_name(i) + "\""
            logging.debug(f'Getting jump: {rule.get("jump", "")}')
            tmp_body += """>""" + rule["rule_body"] + """</td></tr>"""
        tmp_body += """
  <tr><td port="end">end</td></tr>
</table>>];
"""
        output += tmp_body

output += """
}"""
print(output)
