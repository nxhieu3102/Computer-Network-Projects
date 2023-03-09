const STATE_RECORD = ['Initial', 'Record', 'Download']
let stateIndex = 0
let mediaRecorder, chunks = [], audioURL = ''
let audioName

const recordBtn = document.querySelector('#record-button')
const inputText = document.querySelector('#text-input')
const micIcon = recordBtn.firstElementChild;

if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({
        audio: true
    }).then(async (stream) => {
        mediaRecorder = new MediaRecorder(stream)

        mediaRecorder.ondataavailable = (e) => {
            chunks.push(e.data)
        }

        mediaRecorder.onstop = async () => {
            const blob = new Blob(chunks, { 'type': 'audio/mp3; codecs=opus' })
            chunks = []
            audioURL = window.URL.createObjectURL(blob)
            const downloadLink = document.createElement('a')
            downloadLink.href = audioURL
            audioName = 'audio' + Math.floor(Math.random() * 1000);

            downloadLink.setAttribute('download', audioName)
            downloadLink.click()

            setTimeout( async() => {
                console.log("download complete");
                await fetch($SCRIPT_ROOT + '/whisper', {
                    method: 'POST',
                    body: JSON.stringify({ name: audioName + ".mp3" }),
                    mode: 'cors',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                }).then(res => res.json())
                    .then(res => {
                        let message = res.transcript.text
                        inputText.value = message;
                    }).catch((error) => {
                        console.error('Error:', error);
                        inputText.value = '';
                    });
            }, 5000)
        }
    }).catch(error => {
        console.log('Following error has occured : ', error)
    })
} else {
    stateIndex = ''
    application(stateIndex)
}

const startRecord = () => {
    mediaRecorder.start()
}

const stopRecord = async () => {
    mediaRecorder.stop()
}

recordBtn.addEventListener('click', async () => {
    if (micIcon.classList.contains("fa-microphone")) {
        micIcon.classList.remove("fa-microphone");
        micIcon.classList.add("fa-microphone-slash");
        startRecord()
    } else {
        micIcon.classList.add("fa-microphone");
        micIcon.classList.remove("fa-microphone-slash");
        stopRecord()
    }
})