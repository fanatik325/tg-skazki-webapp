document.getElementById("generate").addEventListener("click", async () => {
  const name = document.getElementById("name").value;
  const age = document.getElementById("age").value;
  const interests = document.getElementById("interests").value;

  const tg = window.Telegram.WebApp;
  const user_id = tg?.initDataUnsafe?.user?.id || null;

  if (!name || !age || !interests) {
    alert("Пожалуйста, заполните все поля.");
    return;
  }

  tg.MainButton.setText("Генерация...").show().disable();

  const res = await fetch("https://your-backend.vercel.app/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, age, interests, user_id }),
  });

  const data = await res.json();
  const storyBox = document.getElementById("story");

  tg.MainButton.hide();
  storyBox.classList.remove("hidden");
  storyBox.innerText = data.story || "Ошибка генерации.";
});
