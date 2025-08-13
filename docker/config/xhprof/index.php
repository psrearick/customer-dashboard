<?php
/**
 * XHProf Profiling Interface for Laravel Performance Testing
 *
 * This provides a web interface to view XHProf profiling results
 * generated during Laravel performance testing.
 */

// Configuration
$xhprof_runs_dir = '/var/www/html/storage/logs/xhprof';
$xhprof_url = '/xhprof';

// XHProf library (Composer)
if (file_exists('/var/www/html/vendor/autoload.php')) {
    require_once '/var/www/html/vendor/autoload.php';
}

// File browser for XHProf runs
if (!isset($_GET['run']) || !isset($_GET['source'])) {
    echo "<h1>Laravel Performance Profiling - XHProf Results</h1>";
    echo "<p>Select a profiling run to view detailed performance analysis:</p>";

    if (is_dir($xhprof_runs_dir)) {
        $files = scandir($xhprof_runs_dir);
        $xhprof_files = array_filter($files, function($file) {
            return strpos($file, 'xhprof.') === 0;
        });

        if (empty($xhprof_files)) {
            echo "<p><em>No profiling runs found. Make sure XHProf is enabled and generating profiles.</em></p>";
        } else {
            echo "<ul>";
            foreach ($xhprof_files as $file) {
                $parts = explode('.', $file);
                if (count($parts) >= 3) {
                    $run_id = $parts[1];
                    $source = $parts[2];
                    $url = "?run={$run_id}&source={$source}";
                    echo "<li><a href='{$url}'>{$file}</a> - " . date('Y-m-d H:i:s', filemtime($xhprof_runs_dir . '/' . $file)) . "</li>";
                }
            }
            echo "</ul>";
        }
    } else {
        echo "<p><em>XHProf directory not found: {$xhprof_runs_dir}</em></p>";
    }

    echo "<h2>How to Generate Profiles</h2>";
    echo "<p>Add the following to your Laravel application to generate XHProf profiles:</p>";
    echo "<pre><code>";
    echo "// Start profiling\n";
    echo "if (extension_loaded('xhprof')) {\n";
    echo "    xhprof_enable(XHPROF_FLAGS_CPU + XHPROF_FLAGS_MEMORY);\n";
    echo "}\n\n";
    echo "// Your application code here\n\n";
    echo "// End profiling and save\n";
    echo "if (extension_loaded('xhprof')) {\n";
    echo "    \$xhprof_data = xhprof_disable();\n";
    echo "    \$xhprof_runs = new XHProfRuns_Default();\n";
    echo "    \$run_id = \$xhprof_runs->save_run(\$xhprof_data, 'laravel');\n";
    echo "}\n";
    echo "</code></pre>";

    exit;
}

// XHProf results
$run_id = $_GET['run'];
$source = $_GET['source'];

echo "<h1>XHProf Results: Run {$run_id}</h1>";
echo "<p><a href='?'>← Back to run list</a></p>";

$profile_file = $xhprof_runs_dir . "/xhprof.{$run_id}.{$source}";

if (file_exists($profile_file)) {
    $profile_data = unserialize(file_get_contents($profile_file));

    echo "<h2>Performance Summary</h2>";
    echo "<table border='1' cellpadding='5' cellspacing='0'>";
    echo "<tr><th>Function</th><th>Calls</th><th>Time (μs)</th><th>Memory (bytes)</th></tr>";

    // Sort by exclusive time
    uasort($profile_data, function($a, $b) {
        return ($b['wt'] ?? 0) <=> ($a['wt'] ?? 0);
    });

    $count = 0;
    foreach ($profile_data as $function => $data) {
        if ($count++ > 50) break; // Show top 50 functions

        echo "<tr>";
        echo "<td>" . htmlspecialchars($function) . "</td>";
        echo "<td>" . number_format($data['ct'] ?? 0) . "</td>";
        echo "<td>" . number_format($data['wt'] ?? 0) . "</td>";
        echo "<td>" . number_format($data['mu'] ?? 0) . "</td>";
        echo "</tr>";
    }

    echo "</table>";

} else {
    echo "<p><em>Profile file not found: {$profile_file}</em></p>";
}
