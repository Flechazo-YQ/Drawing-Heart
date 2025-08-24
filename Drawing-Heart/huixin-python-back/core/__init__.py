import os, importlib, logging

coreDir = os.path.dirname(os.path.abspath(__file__))

for (root, _, files) in os.walk(coreDir):
    for file in files:
        if (file.endswith('.py') and not file.startswith('__init__')):
            fullPath = os.path.join(root, file)
            relativePath = os.path.relpath(fullPath, coreDir)
            modulePath = f"core.{ os.path.splitext(relativePath)[0].replace(os.sep, '.') }"

            try:
                importlib.import_module(modulePath)
            except ImportError as e:
                logging.error(f"❌ 自动加载模块 { modulePath } 时失败: { str(e) }")

                