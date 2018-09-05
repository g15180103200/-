/**
 * Created by tarena on 18-8-23.
 */
$(function() {
    var error_name = true;
    var error_phone = true;
    var error_pwd = true;
    var error_cpwd = true;
    var error_email = true;
    var error_check = true;
    var error_code = true;


    $('#user_name').blur(function(){
        check_name();
    });

    $('#user_phone').blur(function(){
        check_phone();
    });

    $('#pwd').blur(function(){
        check_pwd();
    });

    $('#cpwd').blur(function(){
        check_cpwd();
    });

    $('#email').blur(function(){
        check_email();
    });

    $('#allow').click(function(){
        if($(this).is(':checked')){
            $(this).siblings('span').hide();
            error_check = true;
        }else{
            error_check = false;
            $(this).siblings('span').text('请勾选同意');
            $(this).siblings('span').show();
        }
    });

    $('#zphone').click(function(e){
           //发送验证码''
            $.get('/user/check_code/', {uphone:$('#user_phone').val()}, function(msg) {
                console.log("调用成功");
                console.log(msg);
                if(msg.msg=='提交成功'){
                    RemainTime();
                    error_code = true;
                }else{
                    RemainTime();
                    error_code = false;
                }
            },'json');
        });

        var iTime = 60;
        var sTime = ''; 
        function RemainTime(){
            //按钮倒计时
            if (iTime == 0) {
                document.getElementById('zphone').disabled = false;
                sTime="获取验证码";
                iTime = 60;
                document.getElementById('zphone').value = sTime;
                return;
            }else{
                document.getElementById('zphone').disabled = true;
                sTime="重新发送(" + iTime + ")";
                iTime--;
            }
            setTimeout(function() {RemainTime()},1000)
            document.getElementById('zphone').value = sTime;
        }    

        //给表单绑定提交事件
        $('#reg_form').submit(function(){
            check_name();
            check_phone();
            check_pwd();
            check_cpwd();
            check_email();
            if(error_name==true&&error_phone==true&&error_pwd==true&&error_cpwd==true&&error_email ==true&&error_check==true){
                return true;//返回true则提交数据
            }else{
                alert("请输入正确的注册信息!");
                return false;//返回false不提交数据
            }
        });

})


    function check_name(){
        var len = $('#user_name').val().length;
        if(len<5||len>20){
            $('#user_name').next().text('请输入5-20个字符的用户名');
            $('#user_name').next().show();
            error_name = false;
        }else{
            $.get('/user/register_exist/?uname='+$('#user_name').val(),function(data){
                console.log('data:',data)
                // data = JSON.parse(data)
                if(data.status == 1){
                    $('#user_name').next().text('用户名已存在').show();
                    error_name = false;
                }else{
                    if(data.status == 0){                      
                        $('#user_name').next().hide();
                        error_name = true;
                    }else{
                        $('#user_name').next().text('用户名不能含有空格等特殊字符').show();
                        error_name = false;
                    }
                }
            },'json');
        }
    }

    function check_phone(){
        var phone = $('#user_phone').val();
        var pattern = /^((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|166|198|199|(147))\d{8}$/;
        if(phone.length!=11||!pattern.test(phone)){
            $('#user_phone').next().text('请输入正确的手机号码').show();
            error_phone = false;
        }else{
            $.get('/user/register_exist/?uphone='+phone,function(data){
                console.log(data)
                if(data.status == 1){
                    $('#user_phone').next().text('手机号已存在').show();
                    error_phone = false;
                }else{
                    $('#user_phone').next().hide();
                    error_phone = true;
                }
            },'json')
        }
    }

    function check_pwd(){
        var pwd = $('#pwd').val();
        if(/(\s)+/.test(pwd)){
            $('#pwd').next().text('密码不能包含空格').show();
            error_pwd = false;
        }else if(pwd.length<6||pwd.length>18){
            $('#pwd').next().text('请输入6-18位密码').show();
            error_pwd = false;
        }else{
            $('#pwd').next().hide();
            error_pwd = true;
        }
    };

    function check_cpwd() {
        var pwd = $('#pwd').val();
        var cpwd = $('#cpwd').val();
        if(pwd != cpwd){
            $('#cpwd').next().text('两次密码输入不一致').show();
            error_cpwd = false;
        }else{
            $('#cpwd').next().hide();
            error_cpwd = true;
        }
    };

    function check_email() {
        var email = $('#email').val();
        var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
        if(!re.test(email)){
            $('#email').next().text('请输入正确的邮箱').show();
            error_email = false;
        }else{
            $.get('/user/register_exist/?uemail='+email,function(data){
                data = JSON.parse(data);
                if(data.status == 1){
                    $('#email').next().text('该邮箱已注册').show();
                    error_email = false;
                }else{
                    $('#email').next().hide();
                    error_email = true;
                }
            })
        }
    };