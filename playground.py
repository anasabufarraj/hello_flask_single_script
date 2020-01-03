# ------------------------------------------------------------------------------
#  Copyright (c) 2019. Anas Abu Farraj.
# ------------------------------------------------------------------------------

import os

basedir1 = os.path.abspath('app')
basedir2 = os.path.abspath(os.path.dirname(__file__))
print(basedir1)
print(basedir2)

print(os.path.join(basedir1, 'static/uploads', 'image.jpg'))
print(os.path.join(basedir2, 'app/static/uploads', 'image.jpg'))
