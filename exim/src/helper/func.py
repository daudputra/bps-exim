import asyncio

class Func:

    async def close_bannerpage(page):
        """tutup popup banner pada saat masuk ke dalam page"""
        close_button = page.locator('//html/body/div[5]/div/div/div/div/div/div/div[2]/button')

        if not await close_button.is_visible():
            pass
        else:
            await close_button.wait_for(timeout=3000)
            if await close_button.count() > 0:
                await close_button.click()


    async def click_exim(page, placeholder:str):
        """klik type impor atau ekspor"""
        if placeholder == 'ekspor':
            placeholder = 'e'
        elif placeholder == 'impor':
            placeholder = 'i'
        await page.get_by_placeholder(placeholder).click()