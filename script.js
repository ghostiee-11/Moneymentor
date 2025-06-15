// scriptp.js - Core animations and general comic theme interactions

document.addEventListener("DOMContentLoaded", () => {

    // --- Initialize Floating Coins ---
    // This function creates the animated coins in the background.
    // It looks for a div with the ID 'floatingCoins'.
    if (document.getElementById("floatingCoins")) {
        createFloatingCoins(15); // Create 15 coins
    }

    // --- Initialize Module Card Hover Effects ---
    // This applies the thought bubble visibility and panel transforms on hover.
    // It looks for elements with the class 'module-card'.
    const moduleCards = document.querySelectorAll(".module-card");
    moduleCards.forEach((card) => {
        // Add panel animation on hover
        const comicPanel = card.querySelector(".comic-panel");
        if (comicPanel) {
             card.addEventListener("mouseenter", function () {
               // Panel transform is handled by CSS :hover
             });
             card.addEventListener("mouseleave", function () {
               // Panel transform reset is handled by CSS
             });
        }


        // Add thought bubble visibility on hover
        const thoughtBubble = card.querySelector(".thought-bubble");
        if (thoughtBubble) {
            card.addEventListener("mouseenter", function () {
                thoughtBubble.classList.remove("hidden");
                // Optional: Trigger a small animation on the thought bubble itself
                thoughtBubble.style.transform = 'scale(1.1)';
            });

            card.addEventListener("mouseleave", function () {
                thoughtBubble.classList.add("hidden");
                 thoughtBubble.style.transform = 'scale(1)'; // Reset transform
            });
        }
    });

     // --- Initialize Comic Button Effects ---
     // Adds press down/up animation to elements with class 'comic-button'.
    document.querySelectorAll(".comic-button").forEach((button) => {
      // Hover transform is handled by CSS :hover
      button.addEventListener("mousedown", function () {
        this.style.transform = "translateX(2px) translateY(2px)";
        this.style.boxShadow = "2px 2px 0px 0px rgba(0,0,0,0.8)"; // Simulate press depth
      });

      button.addEventListener("mouseup", function () {
        // Return to hover state transform if mouse is still over, otherwise return to default
         if (button.parentElement.parentElement.parentElement.matches(':hover')) { // Check if parent module-card is hovered
              button.style.transform = "scale(1.08)"; // Go back to hover transform
         } else {
              button.style.transform = ""; // Go back to default transform
         }
        this.style.boxShadow = "4px 4px 0px 0px rgba(0,0,0,0.8)"; // Return to default shadow
      });
       // Ensure shadow resets if mouse leaves while pressed (e.g., drag outside and release)
       button.addEventListener("mouseleave", function() {
           if (!button.matches(':active')) { // Only reset if not currently being clicked/held
               this.style.transform = "";
               this.style.boxShadow = "4px 4px 0px 0px rgba(0,0,0,0.8)";
           }
       });
    });


    // NOTE: Logic for specific modules (Dreamboard calculation, Spin Wheel segments, Stock simulation)
    // should live on their respective HTML pages (dreamboard.html, quiz.html, teenvest.html, etc.)
    // and NOT on this main script file, unless they have a specific effect needed here (like the floating coins).

}); // End DOMContentLoaded


// --- Helper Function: Create Floating Coins ---
// Creates a specified number of coin elements and adds them to the container.
function createFloatingCoins(numberOfCoins) {
    const floatingCoinsContainer = document.getElementById("floatingCoins");
    if (!floatingCoinsContainer) return;

    // Use a simple coin emoji or character if you don't have coin image/SVG
    const coinSymbol = '💰'; // Or '⭐', '$', '₹', '🪙'

    for (let i = 0; i < numberOfCoins; i++) {
        const coin = document.createElement("div");
        coin.className = "coin"; // This class needs to be styled in stylesp.css
        coin.textContent = coinSymbol; // Set the coin character/emoji

        // Random positioning and animation timing
        const randomX = Math.random() * 100; // Start position (percentage of width)
        const randomDelay = Math.random() * 8; // Animation delay (seconds)
        const randomDuration = 12 + Math.random() * 8; // Animation duration (seconds) - make it a bit slower/faster

        coin.style.left = `${randomX}%`;
        coin.style.animationDelay = `${randomDelay}s`;
        coin.style.animationDuration = `${randomDuration}s`;

        // Random starting Y position (optional, makes them appear from below the screen)
        coin.style.bottom = `${-10 - (Math.random() * 20)}vh`; // Start 10-30vh below viewport


        floatingCoinsContainer.appendChild(coin);

        // Optional: Remove coins after animation finishes to prevent clutter over time
        // If animation is infinite, this is not needed. The current CSS animation is infinite.
    }
}