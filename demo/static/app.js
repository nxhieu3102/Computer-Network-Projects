class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox : document.querySelector('.chatbox__support'),
            sendButton : document.querySelector('.send__button')
        }

        this.state = false;
        this.messages = [];

        const searchForm = this.args.chatBox.querySelector('#search-form');
        const searchFormInput = searchForm.querySelector('input');

        // The speech recognition interface lives on the browser’s window object
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition; // if none exists -> undefined

        if(SpeechRecognition) {
            console.log("Your Browser supports speech Recognition");
            
            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            // recognition.lang = "en-US";
        
            searchForm.insertAdjacentHTML("beforeend", '<button type="button"><i class="fas fa-microphone"></i></button>');
        
            const micBtn = searchForm.querySelector("button");
            const micIcon = micBtn.firstElementChild;
        
            micBtn.addEventListener("click", micBtnClick);
            function micBtnClick() {
                if(micIcon.classList.contains("fa-microphone")) { // Start Voice Recognition
                    recognition.start(); // First time you have to allow access to mic!
                }
                else {
                    recognition.stop();
                }
            }
        
            recognition.addEventListener("start", startSpeechRecognition); // <=> recognition.onstart = function() {...}
            function startSpeechRecognition() {
                micIcon.classList.remove("fa-microphone");
                micIcon.classList.add("fa-microphone-slash");
                searchFormInput.focus();
                //console.log("Voice activated, SPEAK");
            }
        
            recognition.addEventListener("end", endSpeechRecognition); // <=> recognition.onend = function() {...}
            function endSpeechRecognition() {
                micIcon.classList.remove("fa-microphone-slash");
                micIcon.classList.add("fa-microphone");
                searchFormInput.focus();
                //console.log("Speech recognition service disconnected");
            }
        
            recognition.addEventListener("result", resultOfSpeechRecognition); // <=> recognition.onresult = function(event) {...} - Fires when you stop talking
            function resultOfSpeechRecognition(event) {
                const current = event.resultIndex;
                const transcript = event.results[current][0].transcript;
                
                if(transcript.toLowerCase().trim()==="stop recording") {
                    recognition.stop();
                }
                else if(!searchFormInput.value) {
                    searchFormInput.value = transcript;
                } else if(transcript.toLowerCase().trim()==="go") {
                    searchForm.submit();
                } else if(transcript.toLowerCase().trim()==="reset input") {
                    searchFormInput.value = "";
                } else {
                    searchFormInput.value = transcript;
                    console.log(transcript);
                }
            }
        }
        else {
            console.log("Your Browser does not support speech Recognition");
        }
    }

    display() {
        const {openButton, chatBox, sendButton} = this.args;
        console.log("hello");
        openButton.addEventListener('click', () => this.toggleState(chatBox))
        sendButton.addEventListener('click',() => this.onSendButton(chatBox))

        const node = chatBox.querySelector('input');
        node.addEventListener("keypress",({key : string}) => {
            if (string === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    toggleState(chatbox) {
        this.state = !this.state;

        if (this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value
        if (text1 === "") {
            return;
        }

        let msg1 = {name : "User", message : text1, type : "text"}
        console.log(msg1.message);
        this.messages.push(msg1);
        this.updateChatText(chatbox);
        textField.value = '';

        fetch($SCRIPT_ROOT + '/predict',{
            method: 'POST',
            body : JSON.stringify({message : text1}),
            mode : 'cors',
            headers : {
                'Content-Type' : 'application/json'
            },
        })
        .then(r => r.json())
        .then(r => {
            let msg2 = {name : "GPT", message : r.answer, type : r.type}
            this.messages.push(msg2);
            this.updateChatText(chatbox);
            textField.value = '';
        }).catch((error) => {
            console.error('Error:' , error);
            this.updateChatText(chatbox);
            textField.value = '';
        });
    }

    updateChatText(chatbox) {
        const html = chatbox.querySelector('.chatbox__messages');
        html.innerHTML = '';
        this.messages.slice().reverse().forEach(function(item,index) {
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