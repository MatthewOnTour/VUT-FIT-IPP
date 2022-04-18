<?php

/*      PARSING       */
//checking if any arg is there and how to handle it 
function handle_arguments($argvs){
    $argc = count($argvs);
    $directory_path_arg = FALSE;
    $recursive_arg = FALSE;
    $parse_script_arg = FALSE;
    $int_script_arg = FALSE;
    $parse_only_arg = FALSE;
    $int_only_arg = FALSE;
}


/*      HTML       */

function html_header()
{
    return "<!DOCTYPE html>
                <html lang=\"en\">
                    <head>
                        <meta charset=\"UTF-8\">
                        <title>TESTS</title>
                    </head>
                    <body>
                        <h1 style=\"text-align: center; color: green\">Tests log</h1>\n";
}

function end_html($string)
{
    $res = ($GLOBALS['test_passed_count'] / $GLOBALS['test_count']) * 100;
    $string .= "            <h2 style=\"color: green\">Results: " . round($res, 2) . "%</h2>
            <p style=\"margin-left: 60px\">Succesfull tests: " . $GLOBALS['test_passed_count'] . "</p>
            <p style=\"margin-left: 60px\">All tests: " . $GLOBALS['test_count'] . "</p>
        </body>
    </html>";

    echo $string;
}

/*      MAIN       */
$parse_file = "parse.php";
$interpret_file = "interpret.py";
$directory_path = "";

$test_count = 0;
$test_passed_count = 0;

$arguments = array(FALSE, FALSE, FALSE);

$html_code = html_header();

arguments($argv);

run_all_parse_tests($parse_file);

run_all_int_tests($interpret_file);

end_html($html_code);

?>