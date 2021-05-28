package com.example.examplemod;

import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.init.Blocks;
import net.minecraft.client.Minecraft;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.Mod.EventHandler;
import net.minecraftforge.fml.common.event.FMLInitializationEvent;
import net.minecraftforge.fml.common.event.FMLPreInitializationEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.PlayerEvent.PlayerLoggedInEvent;
import net.minecraftforge.fml.common.gameevent.PlayerEvent.PlayerLoggedOutEvent;
import net.minecraftforge.fml.common.gameevent.TickEvent;
import org.apache.logging.log4j.Logger;
import py4j.GatewayServer;

import java.awt.*;
import java.awt.event.InputEvent;

@Mod(modid = PlayerHandlerMod.MOD_ID, name = PlayerHandlerMod.NAME, version = PlayerHandlerMod.VERSION)
public class PlayerHandlerMod
{
    public static final String MOD_ID = "player_movement_handler_mod";
    public static final String NAME = "Player Handler Mod";
    public static final String VERSION = "1.0";
    //public static final String MC_VERSION = "[1.12.2]";
    //public static final String CLIENT_PROXY_CLASS = "";
    //public static final String COMMON_PROXY_CLASS = "";
    private final PyGatewayServer app;

    private EntityPlayer player;
    private static Logger logger;

    //@Instance(MOD_ID)
    //public static ExampleMod INSTANCE;

    //@SidedProxy(clientSide = CLIENT_PROXY_CLASS, serverSide = COMMON_PROXY_CLASS)

    @EventHandler
    public void preInit(FMLPreInitializationEvent event)
    {
        logger = event.getModLog();
    }

    @EventHandler
    public void init(FMLInitializationEvent event)
    {
        // some example code
        logger.info("DIRT BLOCK >> {}", Blocks.DIRT.getRegistryName());
    }

    public PlayerHandlerMod() {
        // Register ourselves for server and other game events we are interested in
        MinecraftForge.EVENT_BUS.register(this);
        player = null;
        app = new PyGatewayServer();
        GatewayServer gateway = new GatewayServer(app);
        gateway.start();
        System.out.println("Starting py4j server...");



    }

    public static void click(int x, int y) throws AWTException {
        Robot bot = new Robot();
        bot.mouseMove(x, y);
        bot.mousePress(InputEvent.BUTTON1_DOWN_MASK);
        bot.mouseRelease(InputEvent.BUTTON1_DOWN_MASK);
    }

    @SubscribeEvent
    public void onPlayerLoggedIn(PlayerLoggedInEvent event) {
//        app.setPlayerInstance(event.player);
        player = event.player;
    }

    @SubscribeEvent
    public void onPlayerLoggedOut(PlayerLoggedOutEvent event) {
        player = null;
//        app.setPlayerInstance(null);
    }

    @SubscribeEvent
    public void onRenderTick(TickEvent.RenderTickEvent event) throws AWTException {
        if(player == null) { return; }
        EntityPlayer g_player = Minecraft.getMinecraft().player;
        app.setPlayerData(g_player);
//        PlayerHandlerMod.click(1280, 720);
//        double[] test = {-19.5, 88.0, 4.4};
//        logger.info(Integer.toString(app.getMaxHeight(test)));
//        double[] t_pos = {player.posX+10.0D, player.posY, player.posZ};
//        logger.info(Integer.toString(app.getMaxHeight(t_pos)));
    }

}

