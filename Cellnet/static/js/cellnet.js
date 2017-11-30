// cellnet.js : CellNet Main scripts


/** Select Experiment
* Changes text of dropdown when select
* Shows appropiate controls
**/
$(".cn-experiment-dropdown li a").click(function(){
  $(this).parents(".dropdown").find('.btn').html($(this).text() + ' <span class="caret"></span>');
  $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
  alert("EXPERIMENT");
  $(".cn-exp-controls").show();
  $(".cn-experiment-upload-btn").hide();
});


/** Select CellType
* Changes text of dropdown when select
* Changes Visualization
**/
$(".cn-celltype-dropdown li a").click(function(){
  $(this).parents(".dropdown").find('.btn').html($(this).text() + ' <span class="caret"></span>');
  $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
  alert("CELLTYPE");
});
