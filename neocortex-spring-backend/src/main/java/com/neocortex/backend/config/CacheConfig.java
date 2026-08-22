package com.neocortex.backend.config;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import com.neocortex.backend.dto.DiscoveryJob;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.concurrent.TimeUnit;

@Configuration
public class CacheConfig {

    private static final long JOB_RETENTION_HOURS = 24;
    private static final long MAX_CACHED_JOBS = 1000;

    @Bean
    public Cache<String, DiscoveryJob> discoveryJobCache() {
        return Caffeine.newBuilder()
                .expireAfterWrite(JOB_RETENTION_HOURS, TimeUnit.HOURS)
                .maximumSize(MAX_CACHED_JOBS)
                .build();
    }
}
