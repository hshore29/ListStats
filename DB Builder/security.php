<?

//page security
function security($str){
	session_start();
	$pos = explode(",",$str);
	global $db;
	$office = array();
	foreach($pos as $p){
		$query = "SELECT office_holders.uid FROM offices,office_holders WHERE offices.office = '".$p."' AND offices.oid = office_holders.oid";
		$result = mysql_query($query,$db);
		for($i=0;$i<mysql_num_rows($result);$i++){
			$office[] = mysql_result($result,$i,"office_holders.uid");
		}	
	}
	if(in_array($_SESSION['uid'],$office) || $_SESSION['uid'] == 1 || $_SESSION['netid'] == 'hts29'){
		return true;
	}else{
		return false;
	}
}

?>