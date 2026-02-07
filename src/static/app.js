document.addEventListener("DOMContentLoaded", () => {
  const activitiesContainer = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Fetch and display activities
  async function loadActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      activitiesContainer.innerHTML = "";

      Object.entries(activities).forEach(([name, details]) => {
        const card = document.createElement("div");
        card.className = "activity-card";

        const participantsList = details.participants
          .map((p) => `<li>${p}</li>`)
          .join("");
        const participantsHTML =
          details.participants.length > 0
            ? `<ul class="participants-list">${participantsList}</ul>`
            : '<p class="no-participants">No participants yet</p>';

        card.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Available Spots:</strong> ${details.max_participants - details.participants.length}/${details.max_participants}</p>
          <div class="participants-section">
            <h5>Signed Up (${details.participants.length}):</h5>
            ${participantsHTML}
          </div>
        `;

        activitiesContainer.appendChild(card);

        // Add to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesContainer.innerHTML = "<p>Error loading activities</p>";
      console.error("Error:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(
          email
        )}`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (response.ok) {
        messageDiv.className = "message success";
        messageDiv.textContent = data.message;
        messageDiv.classList.remove("hidden");
        signupForm.reset();
        loadActivities();
      } else {
        messageDiv.className = "message error";
        messageDiv.textContent = data.detail;
        messageDiv.classList.remove("hidden");
      }
    } catch (error) {
      messageDiv.className = "message error";
      messageDiv.textContent = "Error signing up";
      messageDiv.classList.remove("hidden");
      console.error("Error:", error);
    }
  });

  // Load activities on page load
  loadActivities();
});
