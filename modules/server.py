#!/usr/bin/env python
""" Server/API class.

Class for the HIAS IoT Agent server/API.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files(the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Contributors:
- Adam Milton-Barker - First version - 2021-5-2

"""

import cv2
import json
import jsonpickle
import os
import requests
import time

from modules.AbstractServer import AbstractServer

from io import BytesIO
from PIL import Image
from flask import Flask, request, Response

class server(AbstractServer):
	""" Server/API class.

	Class for the HIAS IoT Agent server/API.
	"""

	def predict(self, req):
		""" Classifies an image sent via HTTP. """

		if len(req.files) != 0:
			img = Image.open(req.files['file'].stream)
		else:
			img = Image.open(BytesIO(req.data))

		img = self.model.data.reshape(img)

		return self.model.predict(img)

	def start(self):
		""" Starts the server. """

		app = Flask(self.helpers.credentials["iotJumpWay"]["name"])

		@app.route('/Inference', methods=['POST'])
		def Inference():
			""" Responds to HTTP POST requests. """

			self.mqtt.publish("States", {
				"Type": "Prediction",
				"Name": self.helpers.credentials["iotJumpWay"]["name"],
				"State": "Processing",
				"Message": "Processing data"
			})

			message = ""
			prediction = self.predict(request)

			if prediction == 1:
				message = "Acute Lymphoblastic Leukemia detected!"
				diagnosis = "Positive"
			elif prediction == 0:
				message = "Acute Lymphoblastic Leukemia not detected!"
				diagnosis = "Negative"

			self.mqtt.publish("States", {
				"Type": "Prediction",
				"Name": self.helpers.credentials["iotJumpWay"]["name"],
				"State": diagnosis,
				"Message": message
			})

			resp = jsonpickle.encode({
				'Response': 'OK',
				'Message': message,
				'Diagnosis': diagnosis
			})

			return Response(response=resp, status=200, mimetype="application/json")

		app.run(host=self.helpers.credentials["server"]["ip"],
				port=self.helpers.credentials["server"]["port"])
