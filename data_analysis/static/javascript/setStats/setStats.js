document.querySelector("#lessonSearch").oninput = (event) => {
    filterLessons(event.target.value)
}

function filterLessons(containsString) {
    const container = document.querySelector("#lessonContainer")
    container.querySelectorAll(".arrow").forEach((arrow) => {
        arrow.hidden = containsString
    })
    console.log(document.querySelectorAll(".arrow"));
    let matched = false
    containsString = containsString.toLowerCase()
    let isArrow = false
    for (let lessonCard of container.children) {
        if(!isArrow) {
            isArrow = true
            if(getAllTextValues(lessonCard).toLowerCase().includes(containsString)) {
                lessonCard.hidden = false
                matched = true
            } else {
                lessonCard.hidden = true
            }
        }
        else {
            isArrow = false
        }
    }
    if(matched) {
       document.querySelector("#lessonSearch").style.border = ""
    } else {
        document.querySelector("#lessonSearch").style.border = "1px solid red"
    }
}

function getAllTextValues(element) {
    ans = element.textContent
    for (let child of element.children) {
        ans += getAllTextValues(child)
    }
    return ans
}

function HTMLStringToElement(text) {
    const parent = document.createElement('div')
    parent.innerHTML = text
    return parent.firstChild
}


/**
 * 
 * @param {float} point specific number that you want to test
 * @param {string} type name that the server uses to call this (e.g. "averageAttempts")
 * @param {boolean} highMeansHard whether the parameter being high means the lesson is too hard (it'll be red if it's hard, green if it's easy)
 * @returns String to be added on
 */
function withinBounds(point, type, highMeansHard) {
    if (point < bounds[type][0]) {
        //Too small!
        if (highMeansHard) {
            return `&nbsp;<img style="position: relative; top: -2px;" src="/static/images/arrow-down-circle-fill-green.svg" data-toggle="tooltip" data-placement="top" title="This was lower than the rest of the set">`
        }
        return `&nbsp;<img style="position: relative; top: -2px;" src="/static/images/arrow-down-circle-fill-red.svg" data-toggle="tooltip" data-placement="top" title="This was lower than the rest of the set">`
    }
    if (point > bounds[type][1]) {
        //Too big!
        if (highMeansHard) {
            return `&nbsp;<img style="position: relative; top: -2px;" src="/static/images/arrow-up-circle-fill-red.svg" data-toggle="tooltip" data-placement="top" title="This was higher than the rest of the set">`
        }
        return `&nbsp;<img style="position: relative; top: -2px;" src="/static/images/arrow-up-circle-fill-green.svg" data-toggle="tooltip" data-placement="top" title="This was higher than the rest of the set">`
    }
    return ""
}


//Make cards
const container = document.querySelector("#lessonContainer")
let addition
const lessons = lessonSetData["lessons"]
const bounds = lessonSetData["statBounds"]
let index = 0
for (let lesson of lessons) {
    addition = HTMLStringToElement(`<div class="col-3" style="margin: 20px 0px 20px 5px" id="lesson${lesson.lessonIndex}">
    <div class="card">
        <div class="card-body">
            <i class="fas fa-cog" style="float: right"></i>
            <h5 class="card-title">${lesson.title}</h5>
            <h6 class="card-subtitle mb-2 text-muted">${lesson.name}</h6>
            <p class="card-text">
                Average attempts: ${lesson.averageAttempts.toString().substr(0, 4)}${withinBounds(lesson.averageAttempts, "averageAttempts", true)}<br>
                First try rate: ${(100*lesson.firstTryRate).toString().substr(0, 5)}%${withinBounds(lesson.firstTryRate, "firstTryRate", false)}<br>
                <btn type="button" class="btn btn-primary float-right">View Graph</btn>
                Completion rate: ${(100 * lesson.completionRate).toString().substr(0, 5)}%${withinBounds(lesson.completionRate, "completionRate", false)}<br>
                Users: ${lesson.userCount}
            </p>
        </div>
    </div>
</div>`)
    addition.querySelector(".btn").onclick = () => {
        window.location.href = `/data_analysis/data/${lessonSetInfo["id"]}/${lesson.lessonIndex}`
    }
    container.appendChild(addition)
    index++
    if(index != lessons.length) { //so I don't add an arrow going nowhere
        addition = HTMLStringToElement(`<div class="arrow"><svg width="60" height="12"><polygon points="0, 3 50, 3 50, 0 60, 6 50, 12 50, 9 0, 9" fill="gray" /></svg></div>`)
        container.appendChild(addition)
    }
}