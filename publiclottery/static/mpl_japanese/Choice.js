function submitChoices() {
    const amounts = js_vars.amounts;
    const choices = {};
    let allSelected = true;

    for (const amount of amounts) {
        const fieldName = 'choice_' + amount;
        const radios = document.getElementsByName(fieldName);
        let selectedValue = null;

        for (const radio of radios) {
            if (radio.checked) {
                selectedValue = radio.value;
                break;
            }
        }

        if (selectedValue === null) {
            allSelected = false;
            break;
        }
        choices[amount] = selectedValue;
    }

    if (!allSelected) {
        alert("すべての行で選択を行ってください。");
        return;
    }

    // 送信ボタンを無効化
    const btn = document.getElementById('submit-btn');
    if (btn) {
        btn.disabled = true;
        btn.innerText = "送信中...";
    }

    // oTreeのliveSendを使用してサーバーにデータを送る
    liveSend({
        'type': 'submit',
        'choices': choices
    });
}

// サーバーからの応答を受け取る関数
function liveRecv(data) {
    if (data && data.type === 'finished') {
        // oTreeの「次へ」ボタンを自動クリックしてページを遷移させる
        const nextBtn = document.querySelector('.otree-btn-next');
        if (nextBtn) {
            nextBtn.click();
        } else {
            // 万が一ボタンがない場合はフォームを直接サブミット
            document.querySelector('form').submit();
        }
    }
}
