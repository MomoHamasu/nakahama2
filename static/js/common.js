$(function($){

    
    // homeのaeta一覧テーブルをリンクにする
    $(".clickable-row").css("cursor","pointer").on("click",function(){
        location.href = $(this).data("href");
    });


    // homeのプロフィール画像の変更
    $(".sec1btn").on("click",function(){
        $("#up-me-image").show();
    })

    $(".js-popup-close-me").on("click",function(){
        $("#up-me-image").hide();
    ;})


    // addcardの画像変更ポップアップ
    $(".top .parts1 .aetaimage .add_img_change").on("click",function(){
        $("#upimage").show();
    });
    
    $(".js-popup-close img").on("click",function(){
        $("#upimage").hide();
    ;})

    // editcardの画像変更ポップアップ
    $(".top .parts1 .aetaimage .edit_img_change").on("click",function(){
        $("#editimage").show();
    });
    
    $(".js-popup-close img").on("click",function(){
        $("#editimage").hide();
    ;})

    // 画像変更処理
    $("#btn_up_img").on('click', function(){
        if ($("input[name='img_file']").val() == '') {
            return false;
        } else {
            
            $("#form_up_img").submit();
            
        }
    });

    $('.js-modal-open').on('click',function(){
        $('.js-modal').fadeIn();
        return false;
    });
    $('.js-modal-close').on('click',function(){
        $('.js-modal').fadeOut();
        return false;
    });
    $('.js-popup-close').on('click',function(){
        $('.js-modal').fadeOut();
        return false;
    });

});