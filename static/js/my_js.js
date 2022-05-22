//숫자만
function num_only(only_this){
  only_this.value = only_this.value.replace(/[^0-9.]/g, '').replace(/(\..*)\./g, '$1');
}
//600초과불가
function NO_over_600(only_this){
  if(only_this.value>600){
    only_this.value=600;
  }
}

function NO_kid(only_this){
  var adult_year = new Date().getFullYear() - 18;
  if(only_this.value>adult_year){
    only_this.value=adult_year;
  }
}
function NO_spc(str){
  const regex = /^[ㄱ-ㅎ|가-힣|a-z|A-Z|0-9|]+$/;
  return regex.test(str)    // 한글, 영어, 숫자는 true 그외는 false
}

function ONLY_hangul(str){
  const regex = /^[ㄱ-ㅎ|가-힣]+$/;
  return regex.test(str)    // 한글은 true 그외는 false
}

//아이디전송(관리자)
function transmit_id() {    
    var sel = document.getElementById('copy_id');
    var val = sel.options[sel.selectedIndex].value
    console.log(val)
    document.getElementById('user_id').value = val;    
}

//유효성검사(레시지제작)
function valid_dect(){
    row_count = Number($('#row_count').val())   //현재 행의 개수

    var dup_flag = 0;    //중복
    var sum_flag = 0;    //초과
    

    var drinks = [];
    var amount_sum = 0;
    var recipe_name = $('#recipe_name').val();


    // 기존 레시피명 중복인지 판단
    var existing_recipe = $('#existing_recipe').html().split(',')
    existing_recipe.pop() //마지막 콤마 제거
    

    for (var i=0; i<existing_recipe.length; i++){
      if(recipe_name == existing_recipe[i]){
        return alert(`레시피명 '${recipe_name}' 중복`)
      }
    }

    //id가져오기
    for(var i=0; i<row_count; i++){
      drink = $(`#drink${i}`).val();  //val : content 접근
      amount = $(`#drink${i}_amount`).val();
      if(drink=='' || amount=='' || recipe_name==''){return alert('데이터를 입력하세요')}
      else{
        drinks[i] = drink
        amount_sum = amount_sum + Number(amount)
      }
      if (ONLY_hangul(drink)==false){return alert('음료이름(재료)는 한글만 가능')}
    }
    if(NO_spc(recipe_name) == false){
      return alert(`한글, 영어, 숫자만 입력가능`)
    }
   
    
    var dup_drink

    for(var i=0; i<row_count; i++){
      if(drinks[i] == ''){continue;}    //''인경우는 pass
      else{for(var j=i+1; j<row_count; j++){if(drinks[i]==drinks[j]){dup_flag=1; dup_drink=drinks[i];break;}}}  //중복존재시 flag=1, break
      if(dup_flag==1){break;}
    }

    if(amount_sum>=0 && amount_sum<=700){sum_flag=0} //문제없음
    else{sum_flag=1}  //문제있음
    
    var valid_flag = dup_flag|sum_flag;   //OR연산으로 둘다 0인경우에만 0 (문제없음)

    if(valid_flag==0){
      
      //.attr : 속성추가
      $('#recipe_name').attr("readonly",true)          //레시피이름 수정불가
      $('input[type=text]').attr("readonly",true)     //글자 수정불가
      $('input[type=number]').attr("readonly",true)   //숫자 수정불가
      $('#recipe_name').css("background-color", "#D3D3D3")     //레시피제목 색변경
      $('input[type=text]').css("background-color", "#D3D3D3")     //글자수정 색변경
      $('input[type=number]').css("background-color", "#D3D3D3")   //숫자수정 색변경

      $('#append_table_btn').attr("disabled",true)    //행추가 불가
      $('#pop_table_btn').attr("disabled",true)       //행삭제 불가
      $('#valid_dect_btn').attr("disabled",true)      //유효성검사 불가
      $('#recipe_update_btn').attr("disabled",false)  //업데이트 가능
      $('#save_btn').attr("disabled",false)  //제출 가능
    }
    else{
      if(dup_flag==1){return alert(`음료 '${dup_drink}' 중복`)}
      if(amount_sum>700){return alert(`700초과\n현재값 : ${amount_sum}`)}
    }     
}

function recipe_update(){
  row_count = Number($('#row_count').val())
  $('#recipe_name').attr("readonly",false)          //레시피이름 수정불가
  $('input[type=text]').attr("readonly",false)
  $('input[type=number]').attr("readonly",false)
  $('input[type=text]').css("background-color", "#FFFFFF")     //글자수정색변경
  $('input[type=number]').css("background-color", "#FFFFFF")   //숫자수정색변경

  if(row_count>1){$('#pop_table_btn').attr("disabled",false)}
  if(row_count<8){$('#append_table_btn').attr("disabled",false)}
  $('#valid_dect_btn').attr("disabled",false)
  $('#recipe_update_btn').attr("disabled",true)
  $('#save_btn').attr("disabled",true)

}


function append_table(){
  row_count = Number($('#row_count').val())
  $('#pop_table_btn').attr("disabled", false) // 추가시 무조건 하나 삭제가능
  if(row_count<=7){
    $("#recipe").append(`
    <tr id="row${row_count}">
      <td><input type="text" name="drink${row_count}" id="drink${row_count}" placeholder="${row_count}번음료"></td>
      <td><input type="number" name="drink${row_count}_amount" id="drink${row_count}_amount" placeholder="${row_count}번음료양(0~600)" oninput="num_only(this); NO_over_600(this)"></td>
    </tr>
    `)
    
    $('#row_count').val(row_count + 1);
    if(row_count==7){$('#append_table_btn').attr("disabled",true)}  //행추가불가
  }
}


function pop_table(){
  row_count = Number($('#row_count').val())
  $('#append_table_btn').attr("disabled", false) // 삭제시 무조건 하나 추가가능
  $(`#row${row_count-1}`).remove();
  if(row_count-1==1){$('#pop_table_btn').attr("disabled", true)};
  $('#row_count').val(row_count-1);  
}


function update_dect(){
  row_count = Number($('#row_count').val())   //현재 행의 개수
  amount_sum = 0
  sum_flag=0

  // 기존 레시피명 중복인지 판단
  var existing_recipe = $('#existing_recipe').html().split(',')
  existing_recipe.pop() //마지막 콤마 제거
  var old_recipe_name = $('#old_recipe_name').val();
  var new_recipe_name = $('#new_recipe_name').val();
  
  if(NO_spc(new_recipe_name) == false){
    return alert(`한글, 영어, 숫자만 입력가능`)
  }


  for (var i=0; i<existing_recipe.length; i++){

    // 수정안한경우는 상관없음
    if(new_recipe_name==old_recipe_name){
      continue;
    }

    if(new_recipe_name == existing_recipe[i]){
      return alert(`레시피명 '${new_recipe_name}' 중복`)
    }
  }

  for(var i=0; i<row_count; i++){
    amount = $(`#drink${i}_amount`).val();
    if(amount==''){return alert('데이터를 입력하세요')}
    else{
      amount_sum = amount_sum + Number(amount)
    }
  }
    

  if(amount_sum>=0 && amount_sum<=700){sum_flag=0} //문제없음
  else{sum_flag=1}  //문제있음

  if(sum_flag==0){
    $('#update_dect_btn').attr("disabled",true)         
    $('#modify_btn').attr("disabled",false)          
    $('#update_btn').attr("disabled",false)
    $('#new_recipe_name').attr("readonly",true)
    $('#new_recipe_name').css("background-color", "#D3D3D3")   //숫자수정 색변경 
    $('input[type=number]').attr("readonly",true)
    $('input[type=number]').css("background-color", "#D3D3D3")   //숫자수정 색변경       
  }
  else{
    if(amount_sum>700){return alert(`700초과\n현재값 : ${amount_sum}`)}
  }
}

function update_modify(){
  $('#update_dect_btn').attr("disabled",false)          
  $('#modify_btn').attr("disabled",true)          
  $('#update_btn').attr("disabled",true)
  $('#new_recipe_name').attr("readonly",false)
  $('#new_recipe_name').css("background-color", "#FFFFFF")   //숫자수정 색변경      
  $('input[type=number]').attr("readonly",false)
  $('input[type=number]').css("background-color", "#FFFFFF")   //숫자수정색변경
}

function ban_while_making(){
  var recipe_form = document.recipe_form;

  if(confirm('정말로 만드시겠습니까?(중간에 취소 불가)\n\n중간에 새로고침 누르지마세요') == true){
    $('a').removeAttr("href");
    $('input[type=button]').attr("disabled",true);
    $('input[type=submit]').attr("disabled",true);
    recipe_form.submit();
  }
  
}


function back(){
  var sharing_back = document.sharing_back;
  $('#title').attr("required", false);
  $('#content').attr("required", false);
  sharing_back.submit();
  
}

function comment_delete(only_this){

  if(confirm('삭제하시겠습니까?') == true){
    only_this.form.submit()
  }
}