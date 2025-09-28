from flask import Flask, request, render_template
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import io
import base64

app = Flask(__name__)
model = load_model("bone_cancer_model.h5")
IMG_SIZE = (224, 224)


@app.route("/", methods=["GET"])
def about():
    return render_template("about.html")


@app.route("/predict", methods=["GET", "POST"])
def predict():
    result = None
    prob = None
    confidence_value = None
    img_url = None

    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            return render_template("predict.html", result="No file selected")

        # معالجة الصورة بدون حفظ
        img = Image.open(file.stream).convert("RGB")
        img_resized = img.resize(IMG_SIZE)

        # تجهيز للعرض
        buffered = io.BytesIO()
        img_resized.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode()
        img_url = f"data:image/png;base64,{img_b64}"

        # تجهيز للـ model
        x = np.array(img_resized) / 255.0
        x = np.expand_dims(x, axis=0)

        pred_prob = model.predict(x)[0][0]
        print(pred_prob)

        pred_label = "Cancer" if pred_prob > 0.5 else "Normal"
        confidence = pred_prob * 100 if pred_label == "Cancer" else (1 - pred_prob) * 100

        result = f"Prediction: {pred_label}"
        prob = f"Confidence: {confidence:.2f}%"
        confidence_value = round(confidence, 2)

        return render_template("predict.html", result=result, prob=prob,
                               img_path=img_url, confidence_value=confidence_value)

    return render_template("predict.html")


if __name__ == "__main__":
    app.run(debug=True)
