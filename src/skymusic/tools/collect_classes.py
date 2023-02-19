import os, re

theme = 'light'
platforms = ['mobile', 'playstation', 'switch']

svg_dirs = [os.path.join('../resources/original', platform) for platform in platforms]

classes = []

for svg_dir in svg_dirs:
    for basedir, _, files in os.walk(svg_dir):
    
        for file in files:
            if os.path.splitext(file)[1] == '.svg':
                file_path = os.path.join(basedir, file)
                
                with open(file_path, 'r+') as fp:
                    content = fp.read()
                    
                    mos = re.finditer(r'class=(?:\'|")([^\'"]+)',content)
                    
                    for mo in mos:
                        classes += [mo.group(1)]
                        
classes = list(set(classes))
print(classes)
