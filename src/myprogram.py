# To use this CenterNet in your own project, you can
import sys
CENTERNET_PATH ="/home/ubuntu/PycharmProjects/CenterNet-master/src/lib/"
sys.path.insert(0, CENTERNET_PATH)

from detectors.detector_factory import detector_factory
from opts import opts

MODEL_PATH = "/home/ubuntu/PycharmProjects/CenterNet-master/exp/ctdet/head/model_best.pth"
TASK = 'ctdet' # or 'multi_pose' for human pose estimation
opt = opts().init('{} --load_model {}'.format(TASK, MODEL_PATH).split(' '))
detector = detector_factory[opt.task](opt)

img = "/home/ubuntu/PycharmProjects/CenterNet-master/data/test_data/mo_ni_kaoshi/images/1598409731.459005.jpg"
ret = detector.run(img)['results'] #`ret` will be a python dict: `{category_id : [[x1, y1, x2, y2, score], ...], }`
print(ret)