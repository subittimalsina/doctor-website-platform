(function () {
  const form = document.getElementById("aiForm");
  const input = document.getElementById("aiInput");
  const messages = document.getElementById("aiMessages");

  if (!form || !input || !messages) {
    return;
  }

  function addBubble(content, role, metaText) {
    const bubble = document.createElement("div");
    bubble.className = `ai-bubble ${role}`;
    bubble.textContent = content;
    if (metaText) {
      const meta = document.createElement("span");
      meta.className = "ai-meta";
      meta.textContent = metaText;
      bubble.appendChild(meta);
    }
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
  }

  async function sendMessage(text) {
    addBubble(text, "user", "You");

    try {
      const response = await fetch("/ai/message", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok) {
        throw new Error("AI request failed");
      }

      const data = await response.json();
      addBubble(data.reply, "assistant", `Assistant (${data.source})`);
    } catch (error) {
      addBubble(
        "I could not process your request right now. Please try again shortly.",
        "assistant",
        "Assistant (fallback)"
      );
    }
  }

  addBubble(
    "Hello, I can help with appointments, support tickets, and clinic website navigation.",
    "assistant",
    "Assistant"
  );

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) {
      return;
    }
    input.value = "";
    await sendMessage(text);
  });
})();
