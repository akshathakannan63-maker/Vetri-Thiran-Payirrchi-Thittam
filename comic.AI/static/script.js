function showLoading() {

    const button =
        document.getElementById(
            "generateButton"
        );

    const text =
        document.getElementById(
            "buttonText"
        );

    const spinner =
        document.getElementById(
            "loadingSpinner"
        );


    if (!button) {
        return;
    }


    button.disabled = true;


    if (text) {

        text.textContent =
            "Generating Comic...";

    }


    if (spinner) {

        spinner.classList.remove(
            "hidden"
        );

    }

}