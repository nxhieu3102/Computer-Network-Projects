const msg = new SpeechSynthesisUtterance();
let stateVolume = "speaker"
// set the text that you want to convert to speech

// choose a voice for the speech synthesis (optional)
msg.voice = speechSynthesis.getVoices()[0];
// specify additional settings (optional)
msg.volume = 1;
msg.rate = 1;
msg.pitch = 1;

speechSynthesis.cancel()
// call the speech synthesis API to speak the message

class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button'),
            overlay: document.getElementById('overlay')
        }

        this.state = false;
        this.messages = [];

        const searchForm = this.args.chatBox.querySelector('#search-form');
        const searchFormInput = searchForm.querySelector('input');

    }

    closeModal(chatbox) {
        if (chatbox == null) return;
        chatbox.classList.remove('chatbox--active');
        /*const overlay = document.getElementById('overlay');*/
        overlay.classList.remove('active');
        this.state = !this.state;

    }

    display() {
        const _this = this
        const { openButton, chatBox, sendButton, overlay } = this.args;
        overlay.addEventListener('click', () => {
            const temps = document.querySelectorAll('.chatbox--active')
            temps.forEach(temp => {
                _this.closeModal(temp)
            })
        })

        // openButton.addEventListener('click', () => this.toggleState(chatBox))
        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        const node = chatBox.querySelector('input');
        node.addEventListener("keypress", ({ key: string }) => {
            if (string === "Enter") {
                this.onSendButton(chatBox);
            }
        })

    }


    openModal(chatbox) {
        if (chatbox == null) return;
        chatbox.classList.add('chatbox--active');
        /*const overlay = document.getElementById('overlay');*/
        overlay.classList.add('active');
        //openButton.classList.add('active');
    }

    toggleState(chatbox) {
        this.state = !this.state;
        //const chatitem = document.querySelector('.chatbox-item');
        if (this.state) {
            //chatbox.classList.add('chatbox--active');
            this.openModal(chatbox);
            ///chatitem.classList.add('loading');
        } else {
            //chatbox.classList.remove('chatbox--active')
            this.closeModal(chatbox);
            //chatitem.classList.remove('loading');
        }
    }

    async onSendButton(chatbox) {
        speechSynthesis.cancel()
        const textField = chatbox.querySelector('input');
        const text1 = textField.value
        if (text1 === "")
            return;

        let msg1 = { name: "User", message: text1, type: "text" }
        console.log(msg1.message);
        this.messages.push(msg1);
        this.updateChatText(chatbox);
        textField.value = '';

        await fetch($SCRIPT_ROOT + '/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        }).then(res => res.json())
            .then(res => {
                let msg2 = { name: "GPT", message: res.answer, type: res.type }
                msg.text = res.answer;
                if(stateVolume === "speaker")
                    speechSynthesis.speak(msg);
                this.messages.push(msg2);
                this.updateChatText(chatbox);
                textField.value = '';
            }).catch((error) => {
                console.error('Error:', error);
                this.updateChatText(chatbox);
                textField.value = '';
            });
    }

    updateChatText(chatbox) {
        const html = chatbox.querySelector('.chatbox__messages');
        html.innerHTML = '';
        this.messages.slice().reverse().forEach(function (item, index) {
            if (item.name === "GPT") {
                if (item.type === "image") {
                    const imageElement = document.createElement('img');
                    imageElement.src = item.message;
                    imageElement.className = "messages__item messages__item--visitor";
                    html.appendChild(imageElement);
                } else if (item.type === "text") {
                    const textElement = document.createElement('div');
                    textElement.className = "messages__item messages__item--visitor";
                    textElement.textContent = item.message;
                    html.appendChild(textElement);
                }
            } else {
                const textElement = document.createElement('div');
                textElement.className = "messages__item messages__item--operator";
                textElement.textContent = item.message;
                html.appendChild(textElement);
            }
        });
    }
}

const chatbox = new Chatbox();
chatbox.display();

$('.chatbox__header__icon-volume').click(() => {
    const volumeMute = $('.volume-mute')
    const volumeSpeaker = $('.volume-speaker')

    stateVolume = volumeMute.css("display") === "none" ? "speaker" : "mute"


    if (stateVolume === "speaker") {
        speechSynthesis.cancel()
        stateVolume = "mute"
        if(volumeMute.hasClass('dis-none'))
            volumeMute.removeClass('dis-none')
        volumeMute.addClass('dis-block')

        if(volumeSpeaker.hasClass('dis-block'))
            volumeSpeaker.removeClass('dis-block')
        volumeSpeaker.addClass('dis-none')

    } else {
        stateVolume = "speaker"
        if(volumeSpeaker.hasClass('dis-none'))
            volumeSpeaker.removeClass('dis-none')
        volumeSpeaker.addClass('dis-block')

        if(volumeMute.hasClass('dis-block'))
            volumeMute.removeClass('dis-block')
        volumeMute.addClass('dis-none')
    }
})