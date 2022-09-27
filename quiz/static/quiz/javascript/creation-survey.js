const questions = document.querySelector("#questions-formsets");
const maxNQuestions = 10;
const minNQuestions = 5;

function isNumberOfQuestionsValid(n) {
    return questions.childElementCount >= n;
}

function createDeleteButton(func) {
    let button = document.createElement("button");
    button.type = "button";
    button.id = "del-button";
    button.onclick = func;

    let icon = document.createElement("i");
    icon.classList.add("bi");
    icon.classList.add("bi-x-circle");

    button.append(icon);
    return button;
}

function deleteQuestion() {
    this.parentElement.parentElement.remove()
}
function newQuestion() {
    if (isNumberOfQuestionsValid(maxNQuestions)) {
        return;
    }
    
    let lastQuestion = questions.lastElementChild;
    let numberOfQuestion = Number(lastQuestion.id.match(/(\d+)/g)[0])
    
    let newQuestion = lastQuestion.cloneNode(true);
    let questionLegend = newQuestion.querySelector('legend');
    let inputsQuestion = newQuestion.querySelectorAll("input");
    let deleteButton = newQuestion.querySelector("a");

    n = numberOfQuestion + 1;
    newQuestion.id = newQuestion.id.replace(/question-\d+/,`question-${n}`);
    questionLegend.innerText = `Pregunta ${n+1}`;
    for ( const input of inputsQuestion) {
        input.name = input.name.replace(/question-\d+/,`question-${n}`);
        input.id = input.id.replace(/question-\d+/,`question-${n}`);
    }
    
    deleteButton.hidden = false;
    deleteButton.onclick = deleteQuestion;
    questions.append(newQuestion);
    questions.lastElementChild.scrollIntoView();
}
