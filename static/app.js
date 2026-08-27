const imageInput =
    document.getElementById("imageInput")

const detectButton =
    document.getElementById("detectButton")

const previewImage =
    document.getElementById("previewImage")

const resultImage =
    document.getElementById("resultImage")

const resultSection =
    document.getElementById("resultSection")

const detectionCount =
    document.getElementById("detectionCount")

const inferenceTime =
    document.getElementById("inferenceTime")

const detectionsList =
    document.getElementById("detectionsList")

const errorMessage =
    document.getElementById("errorMessage")

const fileInfo =
    document.getElementById("fileInfo")



imageInput.addEventListener("change", () => {

    const file = imageInput.files[0]

    if (!file) {
        return
    }


    fileInfo.textContent =
        `${file.name} • ${(file.size / 1024).toFixed(1)} KB`


    const previewURL =
        URL.createObjectURL(file)

    previewImage.src = previewURL

    previewImage.classList.remove("hidden")

    detectButton.disabled = false

    resultSection.classList.add("hidden")

    errorMessage.textContent = ""

})



detectButton.addEventListener(
    "click",
    async () => {

        const file = imageInput.files[0]

        if (!file) {
            errorMessage.textContent =
                "Please select an image."

            return
        }


        const formData =
            new FormData()

        formData.append(
            "file",
            file
        )


        detectButton.disabled = true
        detectButton.textContent =
            "Detecting..."

        errorMessage.textContent = ""


        try {

            const response =
                await fetch(
                    "/predict",
                    {
                        method: "POST",
                        body: formData
                    }
                )


            const data =
                await response.json()


            if (!response.ok) {

                errorMessage.textContent =
                    data.detail ||
                    "Prediction failed."

                return
            }


            detectionCount.textContent =
                data.count


            inferenceTime.textContent =
                `${data.inference_ms} ms`


            resultImage.src =
                data.annotated_image


            detectionsList.innerHTML = ""


            if (data.detections.length === 0) {

                detectionsList.innerHTML =
                    "<p>No bird or drone detected.</p>"

            } else {

                data.detections.forEach(
                    detection => {

                        const item =
                            document.createElement("div")

                        item.className =
                            "detection-item"


                        const confidence =
                            (
                                detection.confidence * 100
                            ).toFixed(1)


                        item.innerHTML = `
                            <span class="detection-class">
                                ${detection.class}
                            </span>

                            <span class="detection-confidence">
                                ${confidence}% confidence
                            </span>
                        `


                        detectionsList.appendChild(
                            item
                        )
                    }
                )
            }


            resultSection.classList.remove(
                "hidden"
            )

        }

        catch (error) {

            errorMessage.textContent =
                "Unable to connect to the detection server."

        }

        finally {

            detectButton.disabled = false

            detectButton.textContent =
                "Detect Objects"

        }

    }
)