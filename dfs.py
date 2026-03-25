graph={
    'A':['B','C'],
    'B':['D','E'],
    'C':['F'],
    'D':[],
    'E':['F'],
    'F':[]
    }

visited=set()
def dfs(visted,graph,node):
    if node not in visted:
        print(node)
        visited.add(node)
        for neighbour in graph[node]:
            dfs(visted,graph,neighbour)
dfs(visited,graph,'A')
    
