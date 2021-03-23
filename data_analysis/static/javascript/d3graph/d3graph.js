document.querySelector('#graphTitle').innerHTML = `${graph.lesson.name}<br>${graph.lesson.title}`
document.querySelector('#graphCode').innerHTML = graph.lesson.code.replace(/\\r\\n/g, "<br>")
const filter = {}
const userToColor = new Map()
const userCircleRadius = 4
//users that are checked
filter.checkBoxUsers = []
//users in ranked "goodness" order
filter.sliderUsers = []
//users that should be represent by opaqueness in graph (updated each tick)
filter.allowedUsers = []
const userNumber = Object.keys(graph.data.users).length
Object.entries(graph.data.users).forEach((user, index) => {
  filter.sliderUsers.push(user[0])
  userToColor.set(user[0], `hsl(${index * 360 / userNumber}, ${Math.random() * 50 + 50}%, ${Math.random() * 50 + 25}%)`)
})
filter.sliderUsers.sort((a, b) => {
  return graph.data.users[b].attempts - graph.data.users[a].attempts
})
const minSize = 6
const curve = 0.1
const merged = new Map()
let selectedNode = ""

const drag = d3.drag()
  .on("start", function (d) {
    disableSimulationForces()
    if (!d3.event.active) {
      simulation.alphaTarget(0.2).restart();
      userCircleSimulation.alphaTarget(0.2).restart();
    }
    d.fx = d.x
    d.fy = d.y
  })
  .on("drag", function (d) {
    d.fx = d3.event.x
    d.fy = d3.event.y
    //merge preview stuff
    const collidedList = listCollisions(d.id, {
      "x": d3.event.x,
      "y": d3.event.y,
      "r": radius(d)
    })
    const dragged = this
    node.each(function () {
      if (collidedList.includes(this)) {
        mergePreview(this, dragged)
      } else {
        resetPreview(this)
      }
    })
  })
  .on("end", function (d) {
    const collidedList = listCollisions(d.id, {
      "x": d3.event.x,
      "y": d3.event.y,
      "r": radius(d)
    })
    if (collidedList.length) {
      //something collided!
      collidedList.push(this)
      mergeNodes(collidedList)
    }
    if (!d3.event.active) {
      simulation.alpha(0.07).alphaTarget(0).restart()
      userCircleSimulation.alpha(0.07).alphaTarget(0).restart()
      enableSimulationForces()
    }
    d.fx = null;
    d.fy = null;
  });

//forces for the simulation
function boundingBox() {
  let radius
  for (let curr_node of nodes) {
    radius = Math.sqrt(curr_node.appearances) || minSize
    curr_node.x = Math.max(radius + margin.left, Math.min(width - radius - margin.right, curr_node.x));
    curr_node.y = Math.max(radius + margin.top, Math.min(height - radius - margin.bottom, curr_node.y));
  }
}

function userCircleContainPseudoForce(d) {
  const radius = radiusHelper(d.answer.appearances)
  if (Math.sqrt((d.x - d.answer.x) ** 2 + (d.y - d.answer.y) ** 2) + userCircleRadius > radius) {
    const angle = Math.atan2(d.y - d.answer.y, d.x - d.answer.x)
    d.x = Math.cos(angle) * (radius - userCircleRadius) + d.answer.x
    d.y = Math.sin(angle) * (radius - userCircleRadius) + d.answer.y
  }
}

function userCircleGravity() {
  // for(let userCircle of userCircles) {
  //   userCircle.y += 2.3
  // }
}

//called each tick
function updateAllowedUsers() {
  //only users represented in distance slider
  filter.allowedUsers = filter.sliderUsers.slice(0, Math.ceil(document.querySelector("#filterSlider").value ** 2.5 / Object.entries(graph.data.users).length ** 1.5))
  //now by user checkboxes
  if (filter.checkBoxUsers.length) {
    const acceptedUsers = []
    for (let user of filter.checkBoxUsers) {
      if (filter.allowedUsers.includes(user)) {
        acceptedUsers.push(user)
      }
    }
    filter.allowedUsers = acceptedUsers
  }
  //now by demographics
  document.querySelectorAll(".demographic").forEach((box) => {
    if (box.checked) {
      return
    }
    const acceptedUsers = []
    for (let user of filter.allowedUsers) {
      if (box.dataset.class != graph.data.users[user][box.dataset.category]) {
        acceptedUsers.push(user)
      }
    }
    filter.allowedUsers = acceptedUsers
  })
}

//returns the user list that the filter accepts, takes the data of an answer
function filteredUsers(d) {
  allowedUsers = []
  for (let user of d.users) {
    if (filter.allowedUsers.includes(user)) {
      allowedUsers.push(user)
    }
  }
  return allowedUsers
}

function setClick(obj, d) {
  obj.onclick = () => {
    selectedNode = d.name
    document.querySelector("#nodeInfo").style.backgroundColor = fadedColor(d)
    document.querySelector("#nodeName").innerHTML = `Name: ${d.name}`
    document.querySelector("#nodeDistance").textContent = `Distance: ${d.distance}`
    const correct = Math.round(d.score * 100)
    if (correct >= 0 && correct <= 100) {
      //incorrect ans
      document.querySelector("#nodeCorrect").textContent = `Correct: ${Math.round(d.score * 100)}%`
    } else if (correct > 100) {
      //correct ans
      document.querySelector("#nodeDistance").textContent = ""
      document.querySelector("#nodeCorrect").textContent = "Correct Answer"
    } else {
      //gave up
      document.querySelector("#nodeCorrect").textContent = "Correct: N/A"
    }
    document.querySelector("#nodeAppearances").textContent = `Appearances: ${d.appearances}`
    document.querySelector("#splitNodes").hidden = d.mergeList.length < 2
    updateUserList(d)
    //Check to handle empty lesson
    if (d.appearances > 0) {
      restartSimulations()
    } else {
      if (confirm(`Looks like nobody has attempted this lesson yet...
Want to go back?`)) {
        window.history.back()
      }
      simulation.stop()
      userCircleSimulation.stop()
      svg.remove()
    }
  };
  if (d.name == "Start") {
    obj.onclick()
  }
}

function initializeUserList() {
  //set up buttons
  document.querySelector("#selectClear").onclick = () => {
    clearAllUserChecks(false)
  }
  document.querySelector("#selectAll").onclick = () => {
    selectAllUserChecks(true)
  }
  let userString = ""
  for (let user of Object.entries(graph.data.users)) {
    userString += `<div><input type="checkbox" id="${user[0]}">
        <label for="${user[0]}" style="display: block"></label></div>`
  }
  document.querySelector("#userList").innerHTML = userString.substring(0, userString.length - 6)
  document.querySelectorAll("#userList input").forEach((element) => element.onclick = setCheckBoxFilter)
  document.querySelectorAll(".demographic").forEach(element => element.oninput = restartSimulations)
}

function updateUserList(d) {
  const inputs = document.querySelectorAll("#userList input")
  inputs.forEach((element) => {
    element.style.display = "none"
  })
  document.querySelectorAll("#userList label").forEach((element) => {
    element.style.display = "none"
  })
  //count users
  let userMap = new Map()
  for (let user of d.users) {
    if (!userMap.has(user)) {
      userMap.set(user, 1)
    } else {
      userMap.set(user, userMap.get(user) + 1)
    }
  }
  inputs.forEach((element) => {
    for (let user of userMap) {
      if (user[0] == element.id) {
        //show!
        element.style.display = "initial"
        const label = document.querySelector(`#userList label[for="${element.id}"]`)
        label.style.display = "initial"
        //handle multiple occurrences
        if (user[1] > 1) {
          label.textContent = `${graph.data.users[user[0]].name} (${user[1]})`
        } else {
          label.textContent = graph.data.users[user[0]].name
        }
        return
      }
    }
  })
}

function disableSimulationForces() {
  simulation
    .force("link", null)
    .force("charge", null)
    .force("collision", null)
    .force("yVal", null)
    .force("xVal", null)
    .force("bBox", null)
}

function enableSimulationForces() {
  simulation
    .nodes(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(100).strength(0.01))
    .force("charge", d3.forceManyBody().strength(-120))
    .force("collision", d3.forceCollide(radius))
    .force("yVal", d3.forceY((d) => {
      return d.height * (height - margin.top - margin.bottom) + margin.top
    }).strength(1))
    .force("xVal", d3.forceX(width / 2).strength(0.005))
    .force("bBox", boundingBox)
}

function restartSimulations() {
  simulation.restart()
  userCircleSimulation.restart()
}

function initializeSlider() {
  const slider = document.querySelector("#filterSlider")
  filterSlider.min = 1
  filterSlider.value = filterSlider.max = Object.entries(graph.data.users).length
  filterSlider.oninput = restartSimulations
}

function listCollisions(id, circle) {
  let collidedWith = []
  node
    .each(function (d) {
      if (d.id === id) {
        return
      }
      const otherRadius = radius(d)
      const distance = ((d.x - circle.x) ** 2 + (d.y - circle.y) ** 2) ** (1 / 2)
      //check for circles colliding
      if (-Math.abs(circle.r - otherRadius) < distance && distance < circle.r + otherRadius) {
        collidedWith.push(this)
      }
    })
  return collidedWith
}

function initializeMergeList(d) {
  d.mergeList = [d.id]
}

function initializeSplitButton() {
  document.querySelector("#splitNodes").onclick = () => {
    for (let node of document.querySelectorAll(".node")) {
      if (node.__data__.name === selectedNode) {
        unMerge(node)
        return
      }
    }
  }
}

function findNode(id) {
  return merged.get(id) || id
}

/**
 * Merges index 1 into index 0, deletes index 1, then recurses
 * @param toMerge 
 */
function mergeNodes(toMerge) {
  if (checkIllegalMerge(toMerge[0], toMerge[1], true)) {
    return
  }
  connectNodes(toMerge[1], toMerge[0])
  connectLinks(toMerge[1], toMerge[0])
  moveUserCircles(toMerge[1], toMerge[0])
  toMerge[0].__data__.mergeList.push(...toMerge[1].__data__.mergeList)
  if (toMerge.length < 3) {
    //done! click on the new one and refresh its color, add a dashed stroke to let the user know it's been messed with
    toMerge[0].onclick()
    resetPreview(toMerge[0])
    d3.select(toMerge[0]).selectAll(".opaque, .translucent").attr("fill", color)
    d3.select(toMerge[0]).select(".border").attr("stroke", "#000").attr("stroke-dasharray", "5, 3")
    return
  } else {
    //recursive
    toMerge.splice(1, 1)
    mergeNodes(toMerge)
  }
}

function unMerge(toSplit) {
  const newNodesList = toSplit.__data__.mergeList
  //get rid of redirects
  for (let id of newNodesList) {
    merged.delete(id)
  }
  const xCenter = toSplit.__data__.x
  const yCenter = toSplit.__data__.y
  //Delete the old
  d3.select(toSplit).remove()
  removeEdges(toSplit.__data__)
  //Remake the new
  //Get the data of the old nodes
  const nodeDataArray = []
  originalNodes.forEach((node, index) => {
    if (newNodesList.includes(node.id)) {
      nodeDataArray.push(nodes[index] = JSON.parse(JSON.stringify(node)))
      nodes[index].x = xCenter
      nodes[index].y = yCenter
      nodes[index].vx = nodes[index].vy = 0
    }
  })
  moveBackUserCircles(JSON.parse(JSON.stringify(nodeDataArray)), toSplit.__data__.id)
  addNewEdges(newNodesList)
  addNewNodes(nodeDataArray)
  sortZOrder()
  simulation.alpha(.15).alphaTarget(0).restart()
  userCircleSimulation.alpha(.15).alphaTarget(0).restart()
  enableSimulationForces()
}

function removeEdges(nodeData) {
  link
    .each(function (d) {
      if (d.source === nodeData || d.target === nodeData) {
        d3.select(this).remove()
      }
    })
}

function addNewNodes(nodeDataArray) {
  const newNodes = svg.selectAll()
    .data(nodeDataArray)
    .enter()
    .append("g")
    .attr("class", "node")
    .attr("style", "cursor: pointer;")
    .each(function (d) {
      initializeMergeList(d)
      setClick(this, d)
    })
    .call(drag)

  newNodes.append("circle")
    .attr("r", radius)
    .attr("fill", color)
    .attr("opacity", 0.1)
    .attr("class", "translucent")

  newNodes.append("circle")
    .attr("r", radius)
    .attr("fill", color)
    .attr("stroke", "#555")
    .attr("stroke-width", 1)
    .attr("class", "opaque")

  newNodes.append("circle")
    .attr("r", minSize - 2)
    .attr("stroke-width", 0)
    .attr("class", "center")
  node = svg.selectAll(".node")
  newNodes.nodes()[0].onclick()
}

function addNewEdges(nodeIDArray) {
  const linkDataArray = []
  originalLinks.forEach((link, index) => {
    if (nodeIDArray.includes(link.source) || nodeIDArray.includes(link.target)) {
      linkDataArray.push(links[index] = JSON.parse(JSON.stringify(link)))
      links[index].source = findNode(links[index].source)
      links[index].target = findNode(links[index].target)
    }
  })
  const newLinks = svg.selectAll()
    .data(linkDataArray)
    .enter()
    .append("g")
    .attr("fill", "none")
    .attr("class", "link")
    .attr("stroke", "#999")

  newLinks
    .append("path")
    .attr("class", "translucent")
    .attr("stroke-width", d => d.size ** 0.6 + 1)
    .attr("opacity", 0.1)

  newLinks
    .append("path")
    .attr("class", "opaque")

  link = svg.selectAll(".link")
}

function checkIllegalMerge(merge1, merge2, interrupt) {
  //check for gave up
  if (merge1.__data__.score == -1 || merge2.__data__.score == -1) {
    if (interrupt) {
      alert(`Sorry, you can't merge the special "Gave up" node with anything else!`)
      resetPreview(merge1)
      resetPreview(merge2)
    }
    return true
  }
  //check for start
  if (merge1.__data__.name === "Start" || merge2.__data__.name === "Start") {
    if (interrupt) {
      alert(`Sorry, you can't merge the special "Start" node with anything else!`)
      resetPreview(merge1)
      resetPreview(merge2)
    }
    return true
  }
  //check for incorrect/correct merging
  if (Math.sign(merge1.__data__.score - 1.5) != Math.sign(merge2.__data__.score - 1.5)) {
    if (interrupt) {
      alert(`Sorry, you can't merge incorrect and correct nodes together!`)
      resetPreview(merge1)
      resetPreview(merge2)
    }
    return true
  }
  return false
}

function connectNodes(toDelete, parent) {
  const childData = toDelete.__data__
  const parentData = parent.__data__
  parentData.name += `, ${childData.name}`
  //weighted averages
  parentData.height = (parentData.height * parentData.appearances + childData.height * childData.appearances) / (parentData.appearances + childData.appearances)
  //only run for incorrect nodes
  if (parentData.score != 2) {
    if (!isNaN(parentData.distance) && !isNaN(childData.distance)) {
      parentData.distance = Math.round((parentData.distance * parentData.appearances + childData.distance * childData.appearances) * 100 / (parentData.appearances + childData.appearances)) / 100
    } else if (!isNaN(childData.distance)) {
      parentData.distance = childData.distance
    }
    parentData.score = Math.round((parentData.score * parentData.appearances + childData.score * childData.appearances) * 100 / (parentData.appearances + childData.appearances)) / 100
  }
  parentData.appearances += childData.appearances
  parentData.users = parentData.users.concat(childData.users)
  //delete old node
  d3.select(toDelete).remove()
  //set translucent, border size
  d3.select(parent).selectAll(".translucent, .border").attr("r", radius)
  node = d3.selectAll(".node")
}

function connectLinks(toDelete, parent) {
  //set up merged redirects
  for (let id of toDelete.__data__.mergeList) {
    merged.set(id, parent.__data__.id)
  }
  link
    .each(function (d) {
      //check if something interesting should happen
      if (d.source === toDelete.__data__) {
        //link was coming from the merged node
        d.source = parent.__data__
      } else if (d.target === toDelete.__data__) {
        //link was going to the merged node
        d.target = parent.__data__
      } else {
        return
      }
      //something interesting already happened!
      if (d.target === d.source) {
        //don't want this!
        d3.select(this).remove()
        link = d3.selectAll(".link")
        return
      }
      //check to see if there are duplicate links now
      const me = this
      link
        .each(function (otherD) {
          if (this === me) {
            return
          }
          if (d.source === otherD.source && d.target === otherD.target) {
            //duplicates, needs a merge
            //delete one of the links
            d3.select(me).remove()
            link = d3.selectAll(".link")
            //merge the users
            otherD.users = otherD.users.concat(d.users)
          }
        })
    })
}

function moveUserCircles(toDelete, parent) {
  for (let userCircle of userCircles) {
    if (userCircle.answer == toDelete.__data__) {
      userCircle.answer = parent.__data__
    }
  }
}

function moveBackUserCircles(newNodesCopy, parentID) {
  const changeAnswer = (userCircle) => {
    for (let i = 0; i < newNodesCopy.length; i++) {
      for (let j = 0; j < newNodesCopy[i].users.length; j++) {
        if (userCircle.user == newNodesCopy[i].users[j]) {
          //This userCircle can go to this node! Just need to find the current node to match up...
          returnToOriginal(userCircle, newNodesCopy[i].id)
          //Now that that's rectified, I should delete this so I don't do the same thing again
          if (newNodesCopy[i].users.length == 1) {
            //It'll be empty after I delete, best if I delete the whole node
            newNodesCopy.splice(i, 1)
            return
          }
          newNodesCopy[i].users.splice(j, 1)
          return
        }
      }
      //It's fine that I didn't find a user, I can go to the next node
    }
  }
  const returnToOriginal = (userCircle, newNodeCopyID) => {
    for (let node of nodes) {
      if (node.id == newNodeCopyID) {
        //Found it!
        userCircle.answer = node
        return
      }
    }
    console.error("I couldn't find the current node to bind to!");
  }
  for (let userCircle of userCircles) {
    if (userCircle.answer.id == parentID) {
      //we gotta change its answer
      changeAnswer(userCircle)
    }
  }
  if(newNodesCopy) {
    console.error("I wasn't able to bind all the old userCircles!");
  }
}

function mergePreview(node, dragged) {
  if (checkIllegalMerge(node, dragged)) {
    d3.select(node).selectAll(".preview").remove()
    d3.select(node)
      .append("circle")
      .attr("r", previewRadius(node, dragged))
      .attr("fill", "none")
      .attr("class", "preview")
      .attr("stroke", "#ff0000")
      .attr("stroke-width", 1)
      .attr("stroke-dasharray", "5, 3")
    return
  }
  d3.select(node).selectAll(".preview").remove()
  d3.select(node)
    .append("circle")
    .attr("r", previewRadius(node, dragged))
    .attr("fill", "none")
    .attr("class", "preview")
    .attr("stroke", "#000")
    .attr("stroke-width", 1)
    .attr("stroke-dasharray", "5, 3")
}

function previewRadius(node, dragged) {
  return radiusHelper(node.__data__.appearances + dragged.__data__.appearances)
}

function resetPreview(node) {
  d3.select(node).selectAll(".preview").remove()
}

function sortZOrder() {
  svg.selectAll(".node, .link").sort((a, b) => {
    if (a.target || !b.target) {
      return -1
    }
    if (!a.target || b.target) {
      return 1
    }
    return 0
  })
}

function clearAllUserChecks() {
  document.querySelectorAll("#userList input").forEach((element) => {
    element.checked = false
  })
  setCheckBoxFilter()
}

function selectAllUserChecks() {
  let foundUnchecked = false
  document.querySelectorAll("#userList input").forEach((element) => {
    if (element.style.display != "none") {
      if (!element.checked) {
        foundUnchecked = true
      }
    }
  })
  if (!foundUnchecked) {
    document.querySelectorAll("#userList input").forEach((element) => {
      if (element.style.display != "none") {
        element.checked = false
      }
    })
    setCheckBoxFilter()
    return
  }
  document.querySelectorAll("#userList input").forEach((element) => {
    if (element.style.display != "none") {
      element.checked = true
    }
  })
  setCheckBoxFilter()
}

function setCheckBoxFilter() {
  filter.checkBoxUsers = []
  document.querySelectorAll("#userList input").forEach((element) => {
    if (element.checked) {
      filter.checkBoxUsers.push(element.id)
    }
  })
  restartSimulations()
}

function boldSelect(d) {
  if (selectedNode == d.name) {
    return 2.5
  } else {
    return 1
  }
}

function darkSelect(d) {
  if (selectedNode == d.name) {
    return "#000"
  } else {
    return "#AAA"
  }
}

function boldLine(d) {
  if (selectedNode == d.source.name || selectedNode == d.target.name) {
    d3.select(this)
      .attr("stroke", "#000")
  } else {
    d3.select(this)
      .attr("stroke", "#999")
  }
}

function manageOpaqueLink(d) {
  const users = filteredUsers(d).length
  if (users > 0) {
    d3.select(this)
      .attr("stroke-width", users ** 0.6 + 1)
      .attr("marker-end", "url(#OpaqueTriangle")
  } else {
    d3.select(this)
      .attr("stroke-width", 0)
      .attr("marker-end", "url(#TranslucentTriangle")
  }
}

function userCircleOpacity(d) {
  if (filter.allowedUsers.includes(d.user)) {
    return 1
  } else {
    return 0.15
  }
}

function radius(d) {
  return radiusHelper(d.appearances)
}

function radiusHelper(appearances) {
  if (appearances <= 0) {
    return 0
  }
  return appearances ** 0.5 * minSize
}

function color(d) {
  if (d.name == "Gave Up") {
    return "#ff00ff"
  }
  if (d.distance == "No completions") {
    return "#ff0000"
  }
  if (d.distance == 0) {
    return "#00ffff"
  }
  const goodness = (maxDistance - (d.distance - 1) ** 0.7) / (maxDistance)
  return `rgb(${Math.min(255, Math.floor(510 * (1 - goodness)))}, ${Math.min(Math.floor(510 * goodness), 255)}, 0)`
}

function fadedColor(d) {
  if (d.name == "Gave Up") {
    return "#ffB0ff"
  }
  if (d.distance == "No completions") {
    return "#ffB0B0"
  }
  if (d.distance == 0) {
    return "#B0ffff"
  }
  const goodness = (maxDistance - (d.distance - 1) ** 0.7) / (maxDistance)
  return `rgb(${Math.min(255, Math.floor(158 * (2.114 - goodness)))}, ${Math.min(Math.floor(158 * goodness + 176), 255)}, 176)`
}

// set the dimensions of graph, data
const width = 960
const height = 600
const margin = {
  "left": 50,
  "right": 50,
  "top": 50,
  "bottom": 50
}
let links = graph.data.links
//Filter loops
links.forEach((link, index) => {
  if (link.source == link.target) {
    links.splice(index, 1)
  }
})
let nodes = graph.data.nodes
nodes.sort((a, b) => {
  if (!Number.isNaN(Number.parseFloat(a.distance))) {
    if (!Number.isNaN(Number.parseFloat(b.distance))) {
      //normal case
      if (Number.parseFloat(b.distance) - Number.parseFloat(a.distance) != 0) {
        return Number.parseFloat(b.distance) - Number.parseFloat(a.distance)
      } else {
        //Tied in distance, make more often nodes lower
        return a.appearances - b.appearances
      }
    }
    //b is a no completions, "infinite" distance
    return 1
  }
  //a is no completions
  if (!Number.isNaN(Number.parseFloat(b.distance))) {
    return -1
  }
  //Both are no completions, check to see if one is gave up node
  if (a.score < 0) {
    return -1
  } else if (b.score < 0) {
    return 1
  } else {
    //neither are gave up, make more often nodes lower
    return a.appearances - b.appearances
  }
})
// Preferred height
const length = nodes.length - 1
let maxDistance = 0
nodes.forEach((node, index) => {
  if (!Number.isNaN(Number.parseFloat(node.distance))) {
    if (Number.parseFloat(node.distance) > maxDistance) {
      maxDistance = Number.parseFloat(node.distance)
    }
  }
  node.height = index / length
  node.y = node.height * (height - margin.top - margin.bottom) + margin.top + (0.5 - Math.random()) * 100
  node.x = width / 2 + (0.5 - Math.random()) * 100
})
maxDistance--
maxDistance = maxDistance ** 0.7
//deep copies
const originalNodes = JSON.parse(JSON.stringify(nodes))
const originalLinks = JSON.parse(JSON.stringify(links))
//make user circles
let userCircles = []
for (let node of nodes) {
  for (let user of node.users) {
    userCircles.push({
      "answer": node,
      "user": user,
      "x": 0,
      "y": 0
    })
  }
}
/**
 * And now the simulation! (the above stuff should have probably been done server-side)
 */
// forces
const simulation = d3.forceSimulation()
  .nodes(nodes)
  .force("link", d3.forceLink(links).id(d => d.id).distance(100).strength(0.01))
  .force("charge", d3.forceManyBody().strength(-120))
  .force("collision", d3.forceCollide(radius))
  .force("yVal", d3.forceY((d) => {
    return d.height * (height - margin.top - margin.bottom) + margin.top
  }).strength(1))
  .force("xVal", d3.forceX(width / 2).strength(0.005))
  .force("bBox", boundingBox)


const userCircleSimulation = d3.forceSimulation()
  .nodes(userCircles)
  .force("collision", d3.forceCollide(userCircleRadius + 1.6).iterations(20))


//Had to wait until simulation was created for these so they can tell the simulation to restart
initializeUserList()
initializeSlider()
initializeSplitButton()

// append the svg object to the body of the page
const svg = d3.select("#lessonGraph")
  .attr("viewBox", [0, 0, width, height])
  .style("border", "solid 1px black")


const opaqueMarker = d3.select("svg")
  .append('defs')
  .append('marker')
  .attr("id", "OpaqueTriangle")
  .attr("refX", 3)
  .attr("refY", 4)
  .attr("markerUnits", 'userSpaceOnUse')
  .attr("markerWidth", 12)
  .attr("markerHeight", 8)
  .attr("orient", 'auto')
  .append('path')
  .style("fill", "#000000")
  .attr("d", 'M 0 0 12 4 0 8 3 4');

const translucentMarker = d3.select("svg")
  .append('defs')
  .append('marker')
  .attr("id", "TranslucentTriangle")
  .attr("refX", 3)
  .attr("refY", 4)
  .attr("markerUnits", 'userSpaceOnUse')
  .attr("markerWidth", 12)
  .attr("markerHeight", 8)
  .attr("orient", 'auto')
  .append('path')
  .style("fill", "#000000")
  .attr("d", 'M 0 0 12 4 0 8 3 4')
  .attr("opacity", 0.1)

let link = svg.selectAll(".link")
  .data(links)
  .enter()
  .append("g")
  .attr("fill", "none")
  .attr("class", "link")
  .attr("stroke", "#999")

link
  .append("path")
  .attr("class", "translucent")
  .attr("stroke-width", d => d.size ** 0.6 + 1)
  .attr("opacity", 0.1)

link
  .append("path")
  .attr("class", "opaque")

let node = svg.selectAll(".node")
  .data(nodes)
  .enter()
  .append("g")
  .attr("class", "node")
  .attr("style", "cursor: pointer;")
  .each(function (d) {
    initializeMergeList(d)
    setClick(this, d)
  })
  .call(drag)

// Only needed to be able to click on where the opaque used to be
node.append("circle")
  .attr("r", radius)
  .attr("opacity", 0)
  .attr("class", "translucent")
  .attr("stroke", "none")

node.append("circle")
  .attr("r", radius)
  .attr("fill", color)
  .attr("stroke", "#000")
  .attr("stroke-width", 1)
  .attr("class", "opaque")

node.append("circle")
  .attr("r", radius)
  .attr("fill", "none")
  .attr("class", "border")


//user circle has to keep track of its userID and its answer
let userCircle = svg.selectAll(".userCircle")
  .data(userCircles)
  .enter()
  .append("circle")
  .attr("r", userCircleRadius)
  .style("pointer-events", "none")
  .attr("fill", d => userToColor.get(d.user))
  .attr("stroke-width", 0.7)
  .attr("stroke", "#000")


simulation.on("tick", () => {
  updateAllowedUsers()
  node
    .attr("transform", d => `translate(${d.x}, ${d.y})`)
    .attr("stroke-width", boldSelect)
    .attr("stroke", darkSelect)
    .selectAll(".opaque")
    .attr("r", d => radiusHelper(filteredUsers(d).length))

  link
    .selectAll("path")
    .attr("d", d => {
      const angle = Math.atan2(d.target.y - d.source.y, d.target.x - d.source.x)
      const adjRad = radius(d.target) + 6 + minSize
      const targetX = d.target.x - Math.cos(angle) * adjRad
      const targetY = d.target.y - Math.sin(angle) * adjRad
      const distance = Math.sqrt((targetX - d.source.x) ** 2 + (targetY - d.source.y) ** 2)
      const rightAngle = angle + Math.PI / 2
      const middleX = (targetX + d.source.x) / 2 + Math.cos(rightAngle) * curve * distance
      const middleY = (targetY + d.source.y) / 2 + Math.sin(rightAngle) * curve * distance
      return `M ${d.source.x} ${d.source.y} Q ${middleX} ${middleY} ${targetX + Math.cos(rightAngle) * curve * 20} ${targetY + Math.sin(rightAngle) * curve * 20}`
    })
    .each(boldLine)

  link
    .selectAll(".opaque")
    .each(manageOpaqueLink)

  userCircle
    .each(userCircleContainPseudoForce)
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("opacity", userCircleOpacity)
})