// tax_tool.js

// --- Configuration ---
// Make sure this matches the server's ALLOWED_ORIGIN and SERVER_PORT
const BACKEND_URL = 'https://moneymentor-sq50.onrender.com';

// --- DOM Elements ---
const taxForm = document.getElementById('tax-form');
const incomeInput = document.getElementById('income');
const ageInput = document.getElementById('age');
const detailsInput = document.getElementById('details');
const getStrategyButton = document.getElementById('get-strategy-button');
const outputSection = document.getElementById('output-section');
const strategyOutputDiv = document.getElementById('strategy-output');
const loadingIndicator = document.getElementById('loading');
const errorMessageDiv = document.getElementById('error-message');
const outputDisclaimer = document.getElementById('output-disclaimer');


// --- Event Listener ---
taxForm.addEventListener('submit', handleFormSubmit);

// --- Functions ---

// Handles the form submission
async function handleFormSubmit(event) {
    event.preventDefault(); // Prevent default page reload

    // Clear previous outputs and errors
    strategyOutputDiv.innerHTML = '';
    errorMessageDiv.classList.add('hidden');
    outputSection.classList.add('hidden'); // Hide output section until ready

    // Show loading indicator
    loadingIndicator.classList.remove('hidden');
    getStrategyButton.disabled = true; // Disable button while loading

    // Collect data
    const income = incomeInput.value.trim();
    const age = ageInput.value.trim();
    const details = detailsInput.value.trim(); // Optional

    // Basic client-side validation
    if (!income || !age) {
        displayError("Please enter your approximate annual income and age.");
        return; // Stop here if required fields are empty
    }

    const incomeFloat = parseFloat(income);
    const ageInt = parseInt(age, 10);

    if (isNaN(incomeFloat) || incomeFloat < 0) {
         displayError("Please enter a valid positive number for income.");
         incomeInput.focus();
         return;
    }
    if (isNaN(ageInt) || ageInt < 0 || ageInt > 120) {
         displayError("Please enter a valid age (0-120).");
         ageInput.focus();
         return;
    }


    // Prepare data for backend
    const requestData = {
        income: incomeFloat,
        age: ageInt,
        details: details // Send optional details
    };

    try {
        const response = await fetch(`${BACKEND_URL}/get-tax-strategy`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(requestData),
        });

        // Check if the response was successful (status 2xx)
        if (!response.ok) {
            let errorDetails = `HTTP error! status: ${response.status}`;
            try {
                // Attempt to read error message from response body if available
                const errorJson = await response.json();
                errorDetails = errorJson.error || JSON.stringify(errorJson);
            } catch (e) {
                // If response body is not JSON, use status text
                errorDetails = `Server responded with status ${response.status} ${response.statusText}`;
            }
            throw new Error(`Backend request failed: ${errorDetails}`);
        }

        const data = await response.json();

        if (data.strategy) {
            // Display the strategy
            displayStrategy(data.strategy);
        } else if (data.error) {
             // Backend returned an error message in the expected format
            displayError(data.error);
        } else {
            // Unexpected response format
            displayError("Received an unexpected response format from the server.");
            console.error("Unexpected backend response:", data);
        }

    } catch (error) {
        console.error('Fetch error:', error);
        displayError(`Network error or server issue: ${error.message}. Please ensure the backend server is running and accessible.`);
    } finally {
        // Hide loading indicator and re-enable button
        loadingIndicator.classList.add('hidden');
        getStrategyButton.disabled = false;
    }
}

// Displays the generated strategy in the output section
function displayStrategy(strategyText) {
    // Basic formatting (e.g., convert newlines to breaks if needed, though pre-wrap CSS handles this)
    // strategyOutputDiv.innerHTML = strategyText.replace(/\n/g, '<br>'); // Use pre-wrap in CSS instead
    strategyOutputDiv.textContent = strategyText; // Use textContent to prevent XSS

    outputSection.classList.remove('hidden'); // Show the output section
    // Optional: Scroll to the output section
    outputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Displays an error message
function displayError(message) {
    errorMessageDiv.textContent = message;
    errorMessageDiv.classList.remove('hidden');
    // Optional: Scroll to the error message
    errorMessageDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}
