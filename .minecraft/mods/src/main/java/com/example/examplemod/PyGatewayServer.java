package com.example.examplemod;
import net.minecraft.client.Minecraft;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.init.Blocks;
import net.minecraft.util.math.BlockPos;

public class PyGatewayServer {

    private final double[] p_coordinates;
    private EntityPlayer g_player;
//    private boolean startAction;
//    private final float[] targetPosRotation;
    public PyGatewayServer(){
        p_coordinates = new double[5];
        g_player = null;
//        targetPosRotation = new float[5];
//        startAction = false;
    }

    public void setPlayerData(EntityPlayer player){
        g_player = player;
        p_coordinates[0] = player.posX;
        p_coordinates[1] = player.posY;
        p_coordinates[2] = player.posZ;
        p_coordinates[3] = player.rotationYaw;
        p_coordinates[4] = player.rotationPitch;
    }
//    public void setPlayerInstance(EntityPlayer player){
//        g_player = player;
//    }

    public double[] getPlayerData(){
        return p_coordinates;
    }

//    public void setStartAction(boolean flag, float[] target){
//        targetPosRotation[0] = target[0];
//        targetPosRotation[1] = target[1];
//        targetPosRotation[2] = target[2];
//        targetPosRotation[3] = target[3];
//        targetPosRotation[4] = target[4];
//        startAction = flag;
//    }

    public int getMaxHeight(double[] targetPos){
        int maxHeight = (int) g_player.posY - 100;
        double[] fromGroup = new double[3];
        double[] toGroup = new double[3];
        if (targetPos[0] < g_player.posX){
            fromGroup[0] = targetPos[0];
            toGroup[0] = g_player.posX;
        }else{
            fromGroup[0] = g_player.posX;
            toGroup[0] = targetPos[0];
        }
        if (targetPos[2] < g_player.posZ){
            fromGroup[2] = targetPos[2];
            toGroup[2] = g_player.posX;
        }else{
            fromGroup[2] = g_player.posZ;
            toGroup[2] = targetPos[2];
        }
        fromGroup[1] = g_player.posY - 100.0D;
        toGroup[1] = g_player.posY + 100.0D;

        BlockPos from = new BlockPos(fromGroup[0], fromGroup[1], fromGroup[2]);
        BlockPos to = new BlockPos(toGroup[0], toGroup[1], toGroup[2]);
//        g_player.getPosition().add(5, 5, 5)
//        g_player.getPosition().add(-5, -5, -5)
        for (BlockPos s : BlockPos.getAllInBox(from, to)) {
            if(Blocks.AIR != Minecraft.getMinecraft().world.getBlockState(s).getBlock()){
                if (maxHeight < s.getY()){
                    maxHeight = s.getY();
                }
            }
        }
        return maxHeight;
    }

    public void steerPlayerRotation(float targetAngle){
        g_player.setPositionAndRotationDirect(g_player.posX, g_player.posY, g_player.posZ,
                targetAngle, g_player.rotationPitch,
                10, false);
    }

    public void movePlayer(double[] targetPos, int speed){
        System.out.println(speed);
        g_player.setPositionAndRotationDirect(
                targetPos[0],
                targetPos[1],
                targetPos[2],
                g_player.rotationYaw, g_player.rotationPitch,
                speed, false);
    }
}