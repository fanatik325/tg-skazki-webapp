const tg = window.Telegram.WebApp;
tg.expand();

function readFirstChapter() {
  alert("Показать первую главу сказки...");
  tg.MainButton.text = "Продолжить";
  tg.MainButton.show();
}

function getFullStory() {
  alert("Запросить полную сказку...");
  tg.MainButton.text = "Скачать PDF";
  tg.MainButton.show();
}

tg.MainButton.onClick(() => {
  tg.sendData("clicked_main_button");
});
