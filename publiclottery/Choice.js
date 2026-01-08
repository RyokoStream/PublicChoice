function submitChoices() {
  const radios = document.querySelectorAll('input[type="radio"]');
  const choices = {};
  const amounts = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100];
  
  for (const amount of amounts) {
    const selected = document.querySelector(`input[name="choice_${amount}"]:checked`);
    if (!selected) {
      alert(`${amount}円の選択をしてください`);
      return;
    }
    choices[amount] = parseInt(selected.value);
  }
  
  liveSend({type: 'submit', choices: choices});
}

document.getElementById('submit-btn').addEventListener('click', submitChoices);

function liveRecv(data) {
  if (data.redirect) {
    document.getElementById('form').submit();
  }
}
