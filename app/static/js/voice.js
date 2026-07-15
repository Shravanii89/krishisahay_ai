// ===============================
// KrishiSahay AI Voice Assistant
// ===============================

const voiceBtn = document.getElementById("voiceBtn");
const userInput = document.getElementById("userInput");
const chatForm = document.getElementById("chatForm");

if (voiceBtn) {

    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {

        const SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;

        const recognition = new SpeechRecognition();

        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-IN";

        voiceBtn.addEventListener("click", () => {

            recognition.start();

            voiceBtn.classList.add("listening");

            voiceBtn.innerHTML =
                '<i class="fa-solid fa-microphone-lines"></i>';

        });

        recognition.onresult = function(event) {

            const transcript =
                event.results[0][0].transcript;

            userInput.value = transcript;

            voiceBtn.classList.remove("listening");

            voiceBtn.innerHTML =
                '<i class="fa-solid fa-microphone"></i>';

            // Automatically send message
            chatForm.dispatchEvent(new Event("submit"));

        };

        recognition.onerror = function() {

            voiceBtn.classList.remove("listening");

            voiceBtn.innerHTML =
                '<i class="fa-solid fa-microphone"></i>';

            alert("Voice recognition failed.");

        };

        recognition.onend = function() {

            voiceBtn.classList.remove("listening");

            voiceBtn.innerHTML =
                '<i class="fa-solid fa-microphone"></i>';

        };

    } else {

        voiceBtn.style.display = "none";

    }

}