// Function to clear text area
function clearText() {
    document.getElementById("recognized-text").value = "";
}

// Function to convert text to speech
function speakText() {
    let text = document.getElementById("recognized-text").value;
    let gender = document.getElementById("voice-gender").value;
    let utterance = new SpeechSynthesisUtterance(text);

    // Ensure voices are loaded before selecting one
    speechSynthesis.onvoiceschanged = () => {
        let voices = speechSynthesis.getVoices();
        let selectedVoice = voices.find(voice => voice.name.includes(gender === "male" ? "Male" : "Female"));

        if (selectedVoice) utterance.voice = selectedVoice;
        speechSynthesis.speak(utterance);
    };

    speechSynthesis.getVoices(); // Trigger voice loading
}

// Function to exit the application
function exitApp() {
    if (confirm("Are you sure you want to exit?")) {
        window.close();
    }
}

// Fetch predictions periodically
function fetchPredictions() {
    fetch("/predict", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            document.getElementById("recognized-text").value = data.prediction;
        })
        .catch(error => console.error("Error fetching prediction:", error));
}
// Function to convert text to speech automatically
function speakTextAutomatically(text) {
    if (!text) return; // Don't speak if text is empty

    let utterance = new SpeechSynthesisUtterance(text);
    let gender = document.getElementById("voice-gender").value;

    // Set voice based on gender
    let voices = speechSynthesis.getVoices();
    utterance.voice = voices.find(voice => voice.name.includes(gender === "male" ? "Male" : "Female"));

    speechSynthesis.speak(utterance);
}

// Fetch predictions and speak automatically
let lastPrediction = "";  // To avoid repeating the same word multiple times
setInterval(() => {
    fetch("/predict", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            let predictedText = data.prediction;
            let textBox = document.getElementById("recognized-text");

            if (predictedText && predictedText !== lastPrediction) {
                textBox.value = predictedText;
                lastPrediction = predictedText; // Update last spoken word
                speakTextAutomatically(predictedText); // Speak automatically
            }
        })
        .catch(error => console.error("Error fetching prediction:", error));
}, 1000);

