<githubform>


<img src="images/logo.png" alt="OSSHealth" class="logo">
<input type="text" placeholder="GitHub URL" ref="githubURL"/>
<button onclick={ submit }>Analyze</button><br><br>


<script>

this.submit = function (e) {
  var splitURL = this.root.querySelectorAll('input')[0].value.split('/')
  var repo, owner
  if (splitURL.length > 2) {
    owner = splitURL[3]
    repo = splitURL[4]
  } else if (splitURL.length === 2) {
    owner = splitURL[0]
    repo = splitURL[1]
  } else {
    let errorMessage = document.createElement('p')
    errorMessage.style.color = '#f00'
    errorMessage.innerHTML = 'Enter a valid URL'
    this.root.appendChild(errorMessage)
    return
  }
  this.opts.onsubmit(owner, repo)
}

</script>



</githubform>