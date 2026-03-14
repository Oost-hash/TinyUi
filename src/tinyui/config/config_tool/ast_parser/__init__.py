"""AST-based config parser.

Compileert flat widget configs naar gestructureerde Python dataclasses.

Pipeline: Flat DSL → Parser → AST → Normalize → Analyze → Emit → .py files
"""
