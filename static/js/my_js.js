function transmit_id() {    
    var sel = document.getElementById('copy_id');
    var val = sel.options[sel.selectedIndex].value
    console.log(val)
    document.getElementById('user_id').value = val;    
  }