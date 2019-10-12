import os 
from flask import Flask, request, Response, render_template
import jsonpickle
import numpy as np
import cv2

# Initialize the Flask application
app = Flask(__name__)

def count(img):
    seeds = img
    seeds_gray = cv2.cvtColor(seeds, cv2.COLOR_BGR2RGB)
    seeds_gray = cv2.cvtColor(seeds_gray, cv2.COLOR_RGB2GRAY)
    seeds_preprocessed = cv2.GaussianBlur(seeds_gray, (5, 5), 0)

    _, seeds_binary = cv2.threshold(seeds_preprocessed, 120, 255, cv2.THRESH_BINARY)

    seeds_binary = cv2.bitwise_not(seeds_binary)

    # find contours
    seeds_contours, _ = cv2.findContours(seeds_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # make copy of image
    seeds_and_contours = np.copy(seeds)

    # find contours of large enough area
    min_seed_area = 60
    large_contours = [cnt for cnt in seeds_contours if cv2.contourArea(cnt) > min_seed_area]

    # draw contours
    cv2.drawContours(seeds_and_contours, large_contours, -1, (255,0,0))

    # print number of contours
    # print('number of seeds: %d' % len(large_contours))
    return len(large_contours)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')  

# route http posts to this method
@app.route('/', methods=['POST'])
def process():
    file = request.files['image']

    if not file:
        response = {'message': 'no file uploaded'}
        # encode response using jsonpickle
        response_pickled = jsonpickle.encode(response)

        if request.host in request.base_url:
            print("web")
            return render_template('index.html', file=False, init=True)
        else:
            return Response(response=response_pickled, status=200, mimetype="application/json")

    # convert string of image data to uint8
    nparr = np.fromstring(file.read(), np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # do some fancy processing here....
    result = count(img)
    # build a response dict to send back to client
    response = {'message': 'num of seeds = {}'.format(result)
                }
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    if request.host in request.base_url:
        print("web")
        return render_template('index.html', num_seeds=result, file=True, init=True)
    else:
        return Response(response=response_pickled, status=200, mimetype="application/json")


# start flask app
if __name__ == '__main__':
    app.run()