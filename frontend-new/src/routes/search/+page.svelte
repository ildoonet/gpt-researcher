
<script>
  
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import { marked } from "marked";
  import { goto } from '$app/navigation';

  const grayPlaceholderImage = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wcAAwAB/gb8ggAAAABJRU5ErkJggg==';

  export let data;
  let query = data.query;
  let isProMode = writable(data.pro);
  let research = {};

  function handleKeyDown(event) {
    // enter
    if (event.key === 'Enter' && query.trim() !== '') {
      goto(`/search?q=${encodeURIComponent(query)}&pro=${$isProMode ? '1' : '0'}`);
      research = {};
      do_research();
    }
  }

  let do_research = () => {
    // const response = await fetch(`/api/research?q=${encodeURIComponent(query)}`);
    // const response = await fetch(`/api/test?q=${encodeURIComponent(query)}`);

    const eventSource = new EventSource(`/api/research?q=${encodeURIComponent(query)}&pro=${$isProMode ? '1' : '0'}`);
    // const eventSource = new EventSource(`/api/test?q=${encodeURIComponent(query)}`);

    eventSource.onmessage = (event) => {
        const value = JSON.parse(event.data);

        // 데이터가 도착할 때마다 별도로 처리
        Object.assign(research, value);
        research = research;
        if ('report' in research && 'contexts' in research) {
            eventSource.close();
        }
    };

    eventSource.onerror = (event) => {
        console.error("SSE 연결 오류:", event);
        eventSource.close();
    };
  };

  // 첫 번째 줄을 제외하는 함수
  function excludeFirstLine(content) {
    const lines = content.trim().split('\n');

    // 첫 번째 줄 제거
    lines.shift();

    // 두 번째 줄이 '=' 문자로만 이루어진 경우 제거
    if (lines[0] && /^=+$/.test(lines[0].trim())) {
        lines.shift();
    }

    return lines.join('\n');
  }


  onMount(() => {
    do_research();
  })

</script>
  
<main class="p-8 min-h-screen">
  <input
    type="text"
    bind:value={query}
    class="w-full p-2 mb-4 text-3xl font-extrabold border border-gray-300 rounded-md focus:outline-none"
    on:keydown={handleKeyDown}
  />

  <!-- Floating Toggle for Pro Mode -->
  <!-- <label
    class="absolute right-0 top-0 mt-3 mr-3 flex items-center cursor-pointer space-x-2 bg-white p-2 rounded-md shadow-lg"
  >
    <span>Pro Mode</span>
    <input
      type="checkbox"
      bind:checked={$isProMode}
      class="w-4 h-4"
    />
  </label> -->

<div class="flex flex-col lg:flex-row max-w-full">

  <div class="flex-1">
    {#if 'report' in research}
    <div class="pt-3 pb-6">
        <!-- {@html marked(research.report)} -->
        <article class="prose max-w-full"> {@html marked(excludeFirstLine(research['report'])) } </article>
    </div>
    {:else}
    <div class="space-y-2 pb-6 pt-3">
      <div class="h-4 bg-gray-300 rounded"></div>
      <div class="h-4 bg-gray-300 rounded"></div>
      <div class="h-4 bg-gray-300 rounded"></div>
      <div class="h-4 bg-gray-300 rounded"></div>
      <div class="h-4 bg-gray-300 rounded"></div>
      <div class="h-4 bg-gray-300 rounded"></div>
      <div class="h-4 bg-gray-300 rounded"></div>
      <div class="h-4 bg-gray-300 rounded"></div>
      <div class="h-4 bg-gray-300 rounded"></div>
      <div class="h-4 bg-gray-300 rounded"></div>
      <div class="h-4 bg-gray-300 rounded"></div>
      <div class="h-4 bg-gray-300 rounded"></div>
    </div>
    {/if}
  </div>

  
  <div class="pt-3 pl-5 lg:w-[380px] lg:max-w-[380px]">
  {#if 'contexts' in research}

  <div class="absolute h-full w-full pb-5 ">
    <h2 class="mx-auto max-w-container-sm pb-4 font-polysans text-16 leading-120 tracking-2 text-franklin md:pl-60 lg:pl-40">
      Top Stories
    </h2>
    <ol class="relative">
      {#each Object.entries(research.contexts) as [category, stories]}
        {#if stories.length > 0}
        <li>
          <h3 class="font-bold text-lg pt-1">{category}</h3>
          {#each stories as story}
            <li class="group relative mx-auto flex max-w-container-sm flex-row border-b border-gray-31 bg-gray-13 last-of-type:border-b-0 md:mx-0 md:max-w-full md:border-b-0">
              <div class="flex flex-row border-gray-31 py-4 md:flex-row-reverse md:justify-between md:border-b">
                {#if story.Image}
                <div class="mb-auto mr-16 rounded-[3px] border border-solid border-gray-31 md:mr-0">
                  <img
                    src={story.Image}
                    alt={story.Title}
                    class="rounded-sm w-[75px] md:w-[100px] lg:w-[100px]"
                    on:error={(event) => {
                      event.target.src = grayPlaceholderImage;
                    }}
                  />
                </div>
                {/if}
                <div class="max-w-content-block-standard md:w-content-block-compact md:max-w-content-block-compact {story.Image ? "lg:w-[270px] lg:max-w-[270px]" : "lg:max-w-[380px]"} lg:pr-10">
                  <h2 class="font-polysans text-20 font-bold leading-100 tracking-1 md:text-24 lg:text-20">
                    <a href={story.Source} class="group-hover:shadow-underline-franklin">
                      {story.Title}
                    </a>
                  </h2>
                  <div class="relative z-10 inline-block pt-4 font-polysans text-11 leading-140 tracking-15 text-gray-300 dark:text-gray-bd">
                    <div class="inline-block">
                      <a href="#" class="text-10 hover:shadow-underline-inherit mr-8">
                        {story.Relavant}
                      </a>
                    </div>
                    <!-- <div class="inline-block text-gray-63 dark:text-gray-94">
                      <time>{story.date}</time>
                    </div> -->
                  </div>
                </div>
              </div>
            </li>
          {/each}
        </li>
        {/if}
      {/each}
    </ol>
  </div>

  {:else}
      <div class="animate-pulse flex space-x-4">
        <div class="rounded-full bg-gray-300 h-12 w-12"></div>
        <div class="flex-1 space-y-4 py-1">
            <div class="h-4 bg-gray-300 rounded"></div>
            <div class="space-y-2">
                <div class="h-4 bg-gray-300 rounded"></div>
                <div class="h-4 bg-gray-300 rounded"></div>
            </div>
        </div>
      </div>
      <div class="animate-pulse flex space-x-4">
        <div class="rounded-full bg-gray-300 h-12 w-12"></div>
        <div class="flex-1 space-y-4 py-1">
            <div class="h-4 bg-gray-300 rounded"></div>
            <div class="space-y-2">
                <div class="h-4 bg-gray-300 rounded"></div>
                <div class="h-4 bg-gray-300 rounded"></div>
            </div>
        </div>
      </div>
      <div class="animate-pulse flex space-x-4">
        <div class="rounded-full bg-gray-300 h-12 w-12"></div>
        <div class="flex-1 space-y-4 py-1">
            <div class="h-4 bg-gray-300 rounded"></div>
            <div class="space-y-2">
                <div class="h-4 bg-gray-300 rounded"></div>
                <div class="h-4 bg-gray-300 rounded"></div>
            </div>
        </div>
      </div>
  {/if}

  </div>
  </div>

</main>