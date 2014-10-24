
import io

from ..python.ast import NodeVisitor

class SourceGenerator(NodeVisitor):
    def __init__(self, buf):
        self.out = buf
    
    def generic_visit(self, node):
        node_class = node.__class__.__name__
        print(node_class)
    
    def push(self, token):
        self.out.write(token)
        
    def visit_list(self, l):
        for n in l: self.visit(n)
    
    def visit_Expr(self, node):
        self.visit(node.value)
        
    def visit_BinOp(self, node):
        self.visit(node.left)
        self.push(' ')
        self.visit(node.op)
        self.push(' ')
        self.visit(node.right)
        
    def visit_Num(self, node):
        self.push(str(node.n))
        
    def visit_Add(self, node):
        self.push('+')
        
    def visit_Sub(self, node):
        self.push('-')
        
    def visit_Mult(self, node):
        self.push('*')
        
    def visit_Div(self, node):
        self.push('/')
        
    def visit_Name(self, node):
        self.push(node.id)
        
    def visit_Assign(self, node):
        self.visit(node.targets)
        self.push(' = ')
        self.visit(node.value)
        
    def visit_Module(self, node):
        self.push('[MODULE]\n')
        for stmt in node.body:
            self.visit(stmt)
            self.push(';\n')
        self.push('[/MODULE]\n')
    
def from_ast(ast):
    buf = io.StringIO()
    gen = SourceGenerator(buf)
    gen.visit(ast)
    return buf.getvalue()
    
