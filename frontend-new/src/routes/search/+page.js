export async function load({ url }) {
    const query = url.searchParams.get('q');
    const pro = url.searchParams.get('pro', 0);
    return {
        query,
        pro
    };
}