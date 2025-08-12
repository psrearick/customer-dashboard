<?php

namespace App\Http\Controllers;

use App\actions\SetRedisDefaults;
use Illuminate\Http\Response;
use Prometheus\CollectorRegistry;
use Prometheus\RenderTextFormat;
use Prometheus\Storage\Redis;
use Throwable;

class MetricsController extends Controller
{
    private CollectorRegistry $registry;

    public function __construct(
       SetRedisDefaults $setRedisDefaults,
    ) {
        $setRedisDefaults->handle();

        $this->registry = new CollectorRegistry(new Redis());
    }

    /**
     * @throws Throwable
     */
    public function metrics(
        RenderTextFormat $renderer
    ): Response
    {
        $result = $renderer->render($this->registry->getMetricFamilySamples());

        return response($result, 200)
            ->header('Content-Type', RenderTextFormat::MIME_TYPE);
    }
}