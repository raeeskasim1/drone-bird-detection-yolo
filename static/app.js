const tabs =
    document.querySelectorAll(".mode-tab")

const imageMode =
    document.getElementById("imageMode")

const videoMode =
    document.getElementById("videoMode")

const liveMode =
    document.getElementById("liveMode")

tabs.forEach(tab => {

    tab.addEventListener("click", () => {

        tabs.forEach(item => {
            item.classList.remove("active")
        })

        tab.classList.add("active")


        imageMode.classList.add("hidden")
        videoMode.classList.add("hidden")
        liveMode.classList.add("hidden")


        const mode =
            tab.dataset.mode


        if (mode === "image") {
            imageMode.classList.remove("hidden")
        }

        if (mode === "video") {
            videoMode.classList.remove("hidden")
        }

        if (mode === "live") {
            liveMode.classList.remove("hidden")
        }

    })

})

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

// ==============================
// VIDEO TRACKING
// ==============================

const videoInput =
    document.getElementById("videoInput")

const videoFileInfo =
    document.getElementById("videoFileInfo")

const videoPreview =
    document.getElementById("videoPreview")

const trackButton =
    document.getElementById("trackButton")

const videoError =
    document.getElementById("videoError")

const videoResultSection =
    document.getElementById("videoResultSection")

const trackedVideo =
    document.getElementById("trackedVideo")



// When user selects a video
videoInput.addEventListener("change", () => {

    const file = videoInput.files[0]

    if (!file) {
        return
    }


    // Show file information
    videoFileInfo.textContent =
        `${file.name} • ${(file.size / (1024 * 1024)).toFixed(1)} MB`


    // Create temporary browser preview URL
    const previewURL =
        URL.createObjectURL(file)


    videoPreview.src = previewURL

    videoPreview.classList.remove("hidden")


    // Enable tracking button
    trackButton.disabled = false


    // Hide previous result
    videoResultSection.classList.add("hidden")


    videoError.textContent = ""

})

trackButton.addEventListener(
    "click",
    async () => {

        const file =
            videoInput.files[0]


        if (!file) {

            videoError.textContent =
                "Please select a video."

            return
        }


        const formData =
            new FormData()


        formData.append(
            "file",
            file
        )


        trackButton.disabled = true

        trackButton.textContent =
            "Processing video..."

        videoError.textContent = ""


        try {

            const response =
                await fetch(
                    "/track-video",
                    {
                        method: "POST",
                        body: formData
                    }
                )


            const data =
                await response.json()


            if (!response.ok) {

                videoError.textContent =
                    data.detail ||
                    "Video tracking failed."

                return
            }


            trackedVideo.src =
                data.processed_video


            trackedVideo.load()


            videoResultSection.classList.remove(
                "hidden"
            )

        }

        catch (error) {

            console.error(error)

            videoError.textContent =
                "Unable to connect to the tracking server."

        }

        finally {

            trackButton.disabled = false

            trackButton.textContent =
                "Track Objects"

        }

    }
)

const startCameraButton =
    document.getElementById("startCameraButton")

const stopCameraButton =
    document.getElementById("stopCameraButton")

const liveVideo =
    document.getElementById("liveVideo")

const liveView =
    document.getElementById("liveView")

const overlayCanvas =
    document.getElementById("overlayCanvas")

const overlayContext =
    overlayCanvas.getContext("2d")

const liveStatus =
    document.getElementById("liveStatus")

const liveError =
    document.getElementById("liveError")


let cameraStream = null

const liveCanvas =
    document.createElement("canvas")

const liveContext =
    liveCanvas.getContext("2d")

let liveDetectionRunning = false

async function sendLiveFrame() {

    if (!liveDetectionRunning) {
        return
    }

    // Wait until webcam has actual dimensions
    if (
        liveVideo.videoWidth === 0 ||
        liveVideo.videoHeight === 0
    ) {
        setTimeout(sendLiveFrame, 200)
        return
    }


    liveCanvas.width =
        liveVideo.videoWidth

    liveCanvas.height =
        liveVideo.videoHeight


    // Copy current webcam frame into canvas
    liveContext.drawImage(
        liveVideo,
        0,
        0,
        liveCanvas.width,
        liveCanvas.height
    )


    liveCanvas.toBlob(
        async blob => {

            if (!blob) {
                return
            }


            const formData =
                new FormData()

            formData.append(
                "file",
                blob,
                "frame.jpg"
            )


            try {

                const response =
                    await fetch(
                        "/live-detect",
                        {
                            method: "POST",
                            body: formData
                        }
                    )


                const data =
                    await response.json()


                if (response.ok) {

                    overlayCanvas.width =
                        liveVideo.videoWidth

                    overlayCanvas.height =
                        liveVideo.videoHeight


                    // 1. Draw webcam frame on visible canvas
                    overlayContext.drawImage(
                        liveVideo,
                        0,
                        0,
                        overlayCanvas.width,
                        overlayCanvas.height
                    )


                    // 2. Draw YOLO detections on same canvas
                    data.detections.forEach(
                        detection => {

                            const [
                                x1,
                                y1,
                                x2,
                                y2
                            ] = detection.box


                            const width =
                                x2 - x1

                            const height =
                                y2 - y1


                            overlayContext.lineWidth = 3

                            overlayContext.strokeStyle =
                                "#22c55e"


                            overlayContext.strokeRect(
                                x1,
                                y1,
                                width,
                                height
                            )


                            const confidence =
                                (
                                    detection.confidence * 100
                                ).toFixed(1)


                            const label =
                                `Drone ID: ${detection.track_id} | ${confidence}% | Tracked: ${detection.duration}s`


                            overlayContext.font =
                                "18px Arial"

                            overlayContext.fillStyle =
                                "#22c55e"


                            overlayContext.fillText(
                                label,
                                x1,
                                Math.max(y1 - 8, 20)
                            )

                        }
                    )
                }
            }

            catch (error) {

                console.error(
                    "Live detection error:",
                    error
                )

            }


            // Send next frame after this request finishes
            if (liveDetectionRunning) {

                setTimeout(
                    sendLiveFrame,
                    200
                )

            }

        },
        "image/jpeg",
        0.8
    )
}

startCameraButton.addEventListener(
    "click",
    async () => {

        liveError.textContent = ""

        try {

            cameraStream =
                await navigator.mediaDevices.getUserMedia({
                    video: true,
                    audio: false
                })


            liveVideo.srcObject =
                cameraStream


            liveView.classList.remove("hidden")


            startCameraButton.disabled = true

            stopCameraButton.disabled = false


            liveStatus.textContent =
                "Camera active"

            liveDetectionRunning = true

            sendLiveFrame()
        }

        catch (error) {

            console.error(error)

            liveError.textContent =
                "Unable to access the camera."

        }

    }
)

stopCameraButton.addEventListener(
    "click",
    () => {

        liveDetectionRunning = false

        if (cameraStream) {

            cameraStream
                .getTracks()
                .forEach(track => {
                    track.stop()
                })

        }


        liveVideo.srcObject = null

        liveView.classList.add("hidden")


        cameraStream = null


        startCameraButton.disabled = false

        stopCameraButton.disabled = true


        liveStatus.textContent =
            "Camera stopped"


    }
)